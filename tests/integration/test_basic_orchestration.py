# tests/integration/test_basic_orchestration.py
"""
Basic integration tests for the orchestration spine.
"""

import json
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestrator.manifest import load_manifest, ManifestParser
from src.orchestrator.workflow_executor import WorkflowExecutor
from src.models.parameterized_manifest import ParameterizedManifest
from src.models.artifact_reference import ArtifactReference
from src.models.stage_definition import StageDefinition
from src.models.workflow_state import WorkflowState


def test_manifest_loading_and_validation():
    """Test that manifests can be loaded and validated correctly."""
    # Create a temporary manifest file
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test-workflow",
        "name": "Test Workflow",
        "stages": [
            {
                "stageId": "test-stage",
                "agentRole": "echo",
                "dependsOn": [],
                "inputs": [],
                "outputs": []
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        # Test loading manifest
        manifest = load_manifest(manifest_path)
        assert isinstance(manifest, ParameterizedManifest)
        assert manifest.workflow_id == "test-workflow"
        assert manifest.name == "Test Workflow"
        assert len(manifest.stages) == 1
        assert manifest.stages[0].stage_id == "test-stage"
        assert manifest.stages[0].agent_role == "echo"
        
        # Test manifest parser directly
        parser = ManifestParser()
        parsed_dict = parser.load_from_file(manifest_path)
        assert parsed_dict["manifestVersion"] == "1.0.0"
        assert parsed_dict["workflowId"] == "test-workflow"
        
        print("��✓ Manifest loading and validation test passed")
        
    finally:
        # Clean up temporary file
        os.unlink(manifest_path)


def test_manifest_parameter_substitution():
    """Test that parameter substitution works correctly."""
    # Create a temporary manifest file with parameters
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "workflow-{{suffix}}",
        "name": "Test {{workflow_type}}",
        "stages": [
            {
                "stageId": "test-stage",
                "agentRole": "echo",
                "dependsOn": [],
                "inputs": [
                    {
                        "artifactType": "video",
                        "artifactId": "input-video",
                        "location": "{{video_path}}"
                    }
                ],
"outputs": [
                     {
                         "artifactType": "video",
                         "artifactId": "output-video",
                         "version": "1.0.0",
                         "location": "file:///tmp/output-video.mp4"
                     }
                 ]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        # Test loading manifest with parameters
        parameters = {
            "suffix": "test123",
            "workflow_type": "parameterized",
            "video_path": "file:///tmp/test.mp4"
        }
        
        manifest = load_manifest(manifest_path, parameters)
        assert manifest.workflow_id == "workflow-test123"
        assert manifest.name == "Test parameterized"
        assert manifest.stages[0].inputs[0].location == "file:///tmp/test.mp4"
        
        print("��✓ Manifest parameter substitution test passed")
        
    finally:
        # Clean up temporary file
        os.unlink(manifest_path)


def test_artifact_reference_model():
    """Test the ArtifactReference model."""
    # Test valid artifact reference
    artifact = ArtifactReference(
        artifact_type="video",
        artifact_id="test-video",
        version="1.0.0",
        location="file:///tmp/test.mp4",
        producer_stage="test-stage",
        validation_status="pending"
    )
    
    assert artifact.artifact_type == "video"
    assert artifact.artifact_id == "test-video"
    assert artifact.version == "1.0.0"
    assert artifact.location == "file:///tmp/test.mp4"
    assert artifact.producer_stage == "test-stage"
    assert artifact.validation_status == "pending"
    
    # Test serialization
    artifact_dict = artifact.to_dict()
    assert artifact_dict["artifactType"] == "video"
    assert artifact_dict["artifactId"] == "test-video"
    
    # Test deserialization
    artifact_restored = ArtifactReference.from_dict(artifact_dict)
    assert artifact_restored.artifact_type == artifact.artifact_type
    assert artifact_restored.artifact_id == artifact.artifact_id
    
    # Test with_updated_status
    updated_artifact = artifact.with_updated_status("passed")
    assert updated_artifact.validation_status == "passed"
    assert updated_artifact.artifact_id == artifact.artifact_id  # Other fields unchanged
    
    print("��✓ ArtifactReference model test passed")


def test_stage_definition_model():
    """Test the StageDefinition model."""
    # Test valid stage definition
    stage = StageDefinition(
        stage_id="test-stage",
        agent_role="test-agent",
        depends_on=["dep1", "dep2"],
        inputs=[
            ArtifactReference(
                artifact_type="video",
                artifact_id="input",
                version="1.0.0",
                location="file:///input.mp4",
                producer_stage="",
                validation_status="pending"
            )
        ],
        outputs=[
            ArtifactReference(
                artifact_type="video",
                artifact_id="output",
                version="1.0.0",
                location="file:///output.mp4",
                producer_stage="",
                validation_status="pending"
            )
        ]
    )
    
    assert stage.stage_id == "test-stage"
    assert stage.agent_role == "test-agent"
    assert stage.depends_on == ["dep1", "dep2"]
    assert len(stage.inputs) == 1
    assert len(stage.outputs) == 1
    
    # Test dependency checking
    assert not stage.is_ready([])  # No dependencies completed
    assert not stage.is_ready(["dep1"])  # Only one dependency completed
    assert stage.is_ready(["dep1", "dep2"])  # Both dependencies completed
    
    # Test serialization
    stage_dict = stage.to_dict()
    assert stage_dict["stageId"] == "test-stage"
    assert stage_dict["agentRole"] == "test-agent"
    assert stage_dict["dependsOn"] == ["dep1", "dep2"]
    
    # Test deserialization
    stage_restored = StageDefinition.from_dict(stage_dict)
    assert stage_restored.stage_id == stage.stage_id
    assert stage_restored.agent_role == stage.agent_role
    
    print("��✓ StageDefinition model test passed")


def test_workflow_state_model():
    """Test the WorkflowState model."""
    # Test valid workflow state
    state = WorkflowState(
        workflow_id="test-workflow",
        manifest_version="1.0.0",
        name="Test Workflow"
    )
    
    assert state.workflow_id == "test-workflow"
    assert state.manifest_version == "1.0.0"
    assert state.name == "Test Workflow"
    assert state.status == "pending"
    assert len(state.completed_stages) == 0
    
    # Test marking stage as completed
    artifact = ArtifactReference(
        artifact_type="video",
        artifact_id="test-output",
        version="1.0.0",
        location="file:///output.mp4",
        producer_stage="test-stage",
        validation_status="passed"
    )
    
    state.mark_stage_completed("test-stage", [artifact])
    assert state.is_stage_completed("test-stage")
    assert state.get_stage_outputs("test-stage") == [artifact]
    assert state.status == "pending"  # Status doesn't change automatically
    
    # Test marking stage as failed
    state.mark_stage_failed("test-stage")
    assert state.is_stage_failed("test-stage")
    assert state.status == "failed"
    
    # Test serialization
    state_dict = state.to_dict()
    assert state_dict["workflowId"] == "test-workflow"
    assert state_dict["status"] == "failed"
    assert state_dict["failedStage"] == "test-stage"
    
    # Test deserialization
    state_restored = WorkflowState.from_dict(state_dict)
    assert state_restored.workflow_id == state.workflow_id
    assert state_restored.status == state.status
    assert state_restored.is_stage_failed("test-stage")
    
    print("��✓ WorkflowState model test passed")


def run_all_tests():
    """Run all tests."""
    print("Running basic orchestration tests...")
    
    test_manifest_loading_and_validation()
    test_manifest_parameter_substitution()
    test_artifact_reference_model()
    test_stage_definition_model()
    test_workflow_state_model()
    
    print("All tests passed!")


if __name__ == "__main__":
    run_all_tests()