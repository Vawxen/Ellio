# src/orchestrator/dependency_enforcer.py
"""
Dependency enforcer for determining stage execution order.
"""

from typing import List, Dict, Set, Optional
from ..models.stage_definition import StageDefinition
from ..models.workflow_state import WorkflowState


class DependencyEnforcerError(Exception):
    """Base exception for dependency enforcer errors."""
    pass


class DependencyEnforcer:
    """
    Enforces stage dependencies and determines execution order.
    """
    
    def __init__(self, stages: List[StageDefinition]):
        """
        Initialize dependency enforcer with stage definitions.
        
        Args:
            stages: List of stage definitions
        """
        self.stages = {stage.stage_id: stage for stage in stages}
        self._dependency_graph: Dict[str, Set[str]] = {}
        self._reverse_dependency_graph: Dict[str, Set[str]] = {}
        self._build_dependency_graphs()
    
    def _build_dependency_graphs(self) -> None:
        """Build forward and reverse dependency graphs."""
        # Initialize graphs
        for stage_id in self.stages:
            self._dependency_graph[stage_id] = set()
            self._reverse_dependency_graph[stage_id] = set()
        
        # Build graphs
        for stage_id, stage in self.stages.items():
            for dep in stage.depends_on:
                if dep not in self.stages:
                    raise DependencyEnforcerError(
                        f"Stage {stage_id} depends on unknown stage: {dep}"
                    )
                self._dependency_graph[stage_id].add(dep)
                self._reverse_dependency_graph[dep].add(stage_id)
        
        # Check for circular dependencies
        self._check_for_cycles()
    
    def _check_for_cycles(self) -> None:
        """Check for circular dependencies in the graph."""
        # Using Kahn's algorithm for cycle detection
        in_degree = {stage_id: len(deps) for stage_id, deps in self._dependency_graph.items()}
        queue = [stage_id for stage_id in in_degree if in_degree[stage_id] == 0]
        topological_order = []
        
        while queue:
            node = queue.pop(0)
            topological_order.append(node)
            
            for dependent in self._reverse_dependency_graph[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(topological_order) != len(self.stages):
            raise DependencyEnforcerError("Circular dependency detected in stage definitions")
    
    def get_ready_stages(self, completed_stages: List[str]) -> List[StageDefinition]:
        """
        Get stages whose dependencies are satisfied.
        
        Args.
            completed_stages: List of stage IDs that have completed successfully
            
        Returns:
            List of StageDefinition instances that are ready to execute
        """
        completed_set = set(completed_stages)
        ready_stages = []
        
        for stage_id, stage in self.stages.items():
            # Skip if already completed
            if stage_id in completed_set:
                continue
            
            # Check if all dependencies are completed
            dependencies = self._dependency_graph[stage_id]
            if dependencies.issubset(completed_set):
                ready_stages.append(stage)
        
        return ready_stages
    
    def get_remaining_dependencies(self, stage_id: str, 
                                 completed_stages: List[str]) -> List[str]:
        """
        Get remaining dependencies for a stage.
        
        Args:
            stage_id: ID of the stage to check
            completed_stages: List of stage IDs that have completed successfully
            
        Returns:
            List of dependency stage IDs that are not yet completed
        """
        if stage_id not in self.stages:
            raise DependencyEnforcerError(f"Unknown stage: {stage_id}")
        
        completed_set = set(completed_stages)
        dependencies = self._dependency_graph[stage_id]
        remaining = dependencies - completed_set
        return list(remaining)
    
    def is_stage_ready(self, stage_id: str, completed_stages: List[str]) -> bool:
        """
        Check if a stage's dependencies are satisfied.
        
        Args:
            stage_id: ID of the stage to check
            completed_stages: List of stage IDs that have completed successfully
            
        Returns:
            True if all dependencies are satisfied, False otherwise
        """
        if stage_id not in self.stages:
            raise DependencyEnforcerError(f"Unknown stage: {stage_id}")
        
        completed_set = set(completed_stages)
        dependencies = self._dependency_graph[stage_id]
        return dependencies.issubset(completed_set)
    
    def get_execution_order(self) -> List[str]:
        """
        Get a topological ordering of stages for execution.
        
        Returns:
            List of stage IDs in topological order
            
        Raises:
            DependencyEnforcerError: If circular dependency exists
        """
        # Kahn's algorithm for topological sorting
        in_degree = {stage_id: len(deps) for stage_id, deps in self._dependency_graph.items()}
        queue = [stage_id for stage_id in in_degree if in_degree[stage_id] == 0]
        topological_order = []
        
        while queue:
            node = queue.pop(0)
            topological_order.append(node)
            
            for dependent in self._reverse_dependency_graph[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(topological_order) != len(self.stages):
            raise DependencyEnforcerError("Circular dependency detected in stage definitions")
        
        return topological_order
    
    def get_stage_definition(self, stage_id: str) -> Optional[StageDefinition]:
        """
        Get stage definition by ID.
        
        Args:
            stage_id: ID of the stage
            
        Returns:
            StageDefinition if found, None otherwise
        """
        return self.stages.get(stage_id)