# tests/unit_test_manifest.py
"""
Unit tests for manifest parser and validator.
"""

import json
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestrator.manifest import (
    load_manifest, 
    ManifestParser, 
    ManifestError, 
    ManifestValidationError, 
    ManifestVersionError
)
from src.models.parameterized_manifest import ParameterizedManifest
from src.models.artifact_reference import ArtifactReference
from src.models.stage_definition import StageDefinition

def test_manifest_load_missing_file():
    """Test loading a manifest from a non-existent file."""
    try:
        load_manifest("non_existent_file.json")
        assert False, "Should have raised ManifestError"
    except ManifestError as e:
        assert "not found" in str(e)
        print("✓ Manifest loading missing file test passed")

def test_manifest_load_invalid_json():
    """Test loading a manifest with invalid JSON."""
    # Create a temporary file with invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{ invalid json }')
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestError"
    except ManifestError as e:
        assert "Invalid JSON" in str(e)
        print("✓ Manifest loading invalid JSON test passed")
    finally:
        os.unlink(manifest_path)

def test_manifest_missing_required_fields():
    """Test loading a manifest missing required fields."""
    # Test missing manifestVersion
    manifest_data = {
        "workflowId": "test",
        "name": "Test",
        "stages": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "manifestVersion" in str(e)
        print("✓ Manifest missing manifestVersion test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test missing workflowId
    manifest_data = {
        "manifestVersion": "1.0.0",
        "name": "Test",
        "stages": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "workflowId" in str(e)
        print("✓ Manifest missing workflowId test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test missing name
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "stages": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "name" in str(e)
        print("✓ Manifest missing name test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test missing stages
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "stages" in str(e)
        print("✓ Manifest missing stages test passed")
    finally:
        os.unlink(manifest_path)

def test_manifest_invalid_field_types():
    """Test loading a manifest with invalid field types."""
    # Test manifestVersion not string
    manifest_data = {
        "manifestVersion": 1.0,  # Should be string
        "workflowId": "test",
        "name": "Test",
        "stages": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "manifestVersion must be a string" in str(e)
        print("✓ Manifest invalid manifestVersion type test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test stages not array
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": {}  # Should be array
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "stages must be an array" in str(e)
        print("✓ Manifest invalid stages type test passed")
    finally:
        os.unlink(manifest_path)

def test_manifest_stage_validation():
    """Test validation of individual stages."""
    # Test stage missing stageId
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": [
            {
                "agentRole": "test",
                # missing stageId
                "inputs": [],
                "outputs": []
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "stageId" in str(e)
        print("✓ Manifest stage missing stageId test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test stage missing agentRole
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": [
            {
                "stageId": "test",
                # missing agentRole
                "inputs": [],
                "outputs": []
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "agentRole" in str(e)
        print("✓ Manifest stage missing agentRole test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test stage with invalid dependsOn (not array)
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": [
            {
                "stageId": "test",
                "agentRole": "test",
                "dependsOn": "not-an-array",  # Should be array
                "inputs": [],
                "outputs": []
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "dependsOn must be an array" in str(e)
        print("✓ Manifest stage invalid dependsOn type test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test stage with invalid inputs (not array)
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": [
            {
                "stageId": "test",
                "agentRole": "test",
                "dependsOn": [],
                "inputs": "not-an-array",  # Should be array
                "outputs": []
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "inputs must be an array" in str(e)
        print("✓ Manifest stage invalid inputs type test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test stage with invalid outputs (not array)
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": [
            {
                "stageId": "test",
                "agentRole": "test",
                "dependsOn": [],
                "inputs": [],
                "outputs": "not-an-array"  # Should be array
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "outputs must be an array" in str(e)
        print("✓ Manifest stage invalid outputs type test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test stage with invalid qualityGates (not array)
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": [
            {
                "stageId": "test",
                "agentRole": "test",
                "dependsOn": [],
                "inputs": [],
                "outputs": [],
                "qualityGates": "not-an-array"  # Should be array
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "qualityGates must be an array" in str(e)
        print("✓ Manifest stage invalid qualityGates type test passed")
    finally:
        os.unlink(manifest_path)

def test_manifest_artifact_reference_validation():
    """Test validation of artifact references in inputs/outputs."""
    # Test input missing artifactType
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": [
            {
                "stageId": "test",
                "agentRole": "test",
                "dependsOn": [],
                "inputs": [
                    {
                        # missing artifactType
                        "artifactId": "test",
                        "version": "1.0.0",
                        "location": "test"
                    }
                ],
                "outputs": []
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "artifactType" in str(e)
        print("✓ Manifest input missing artifactType test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test input missing artifactId
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": [
            {
                "stageId": "test",
                "agentRole": "test",
                "dependsOn": [],
                "inputs": [
                    {
                        "artifactType": "test",
                        # missing artifactId
                        "version": "1.0.0",
                        "location": "test"
                    }
                ],
                "outputs": []
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "artifactId" in str(e)
        print("✓ Manifest input missing artifactId test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test input with invalid version type
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": [
            {
                "stageId": "test",
                "agentRole": "test",
                "dependsOn": [],
                "inputs": [
                    {
                        "artifactType": "test",
                        "artifactId": "test",
                        "version": 1.0,  # Should be string
                        "location": "test"
                    }
                ],
                "outputs": []
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "version must be a string" in str(e)
        print("✓ Manifest input invalid version type test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test input with invalid location type
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": [
            {
                "stageId": "test",
                "agentRole": "test",
                "dependsOn": [],
                "inputs": [
                    {
                        "artifactType": "test",
                        "artifactId": "test",
                        "version": "1.0.0",
                        "location": 1.0  # Should be string
                    }
                ],
                "outputs": []
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "location must be a string" in str(e)
        print("✓ Manifest input invalid location type test passed")
    finally:
        os.unlink(manifest_path)

def test_manifest_quality_gate_validation():
    """Test validation of quality gates."""
    # Test quality gate missing gateId
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": [
            {
                "stageId": "test",
                "agentRole": "test",
                "dependsOn": [],
                "inputs": [],
                "outputs": [],
                "qualityGates": [
                    {
                        # missing gateId
                        "type": "schemaValidation"
                    }
                ]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "gateId" in str(e)
        print("✓ Manifest quality gate missing gateId test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test quality gate missing type
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": [
            {
                "stageId": "test",
                "agentRole": "test",
                "dependsOn": [],
                "inputs": [],
                "outputs": [],
                "qualityGates": [
                    {
                        "gateId": "test",
                        # missing type
                    }
                ]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "type" in str(e)
        print("✓ Manifest quality gate missing type test passed")
    finally:
        os.unlink(manifest_path)
    
    # Test quality gate with invalid config type
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test",
        "name": "Test",
        "stages": [
            {
                "stageId": "test",
                "agentRole": "test",
                "dependsOn": [],
                "inputs": [],
                "outputs": [],
                "qualityGates": [
                    {
                        "gateId": "test",
                        "type": "schemaValidation",
                        "config": "not-an-object"  # Should be object
                    }
                ]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestValidationError"
    except ManifestValidationError as e:
        assert "config must be an object" in str(e)
        print("✓ Manifest quality gate invalid config type test passed")
    finally:
        os.unlink(manifest_path)

def test_manifest_unsupported_version():
    """Test loading a manifest with unsupported version."""
    manifest_data = {
        "manifestVersion": "2.0.0",  # Not supported
        "workflowId": "test",
        "name": "Test",
        "stages": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        load_manifest(manifest_path)
        assert False, "Should have raised ManifestVersionError"
    except ManifestVersionError as e:
        assert "Unsupported manifest version" in str(e)
        print("✓ Manifest unsupported version test passed")
    finally:
        os.unlink(manifest_path)

def test_manifest_parameter_substitution():
    """Test parameter substitution in manifests."""
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
                        "version": "1.0.0"
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
        
        print("✓ Manifest parameter substitution test passed")
        
        # Test missing parameter
        try:
            load_manifest(manifest_path, {"suffix": "test123"})  # Missing workflow_type and video_path
            assert False, "Should have raised ManifestError"
        except Exception as e:
            assert "Parameter not found" in str(e)
            print("✓ Manifest missing parameter test passed")
            
    finally:
        # Clean up temporary file
        os.unlink(manifest_path)

def test_manifest_to_model_conversion():
    """Test conversion from manifest dictionary to ParameterizedManifest model."""
    manifest_data = {
        "manifestVersion": "1.0.0",
        "workflowId": "test-workflow",
        "name": "Test Workflow",
        "description": "A test workflow",
        "stages": [
            {
                "stageId": "stage1",
                "agentRole": "test-agent",
                "dependsOn": [],
                "inputs": [
                    {
                        "artifactType": "video",
                        "artifactId": "input",
                        "version": "1.0.0",
                        "location": "file:///input.mp4"
                    }
                ],
                "outputs": [
                    {
                        "artifactType": "video",
                        "artifactId": "output",
                        "version": "1.0.0",
                        "location": "file:///output.mp4"
                    }
                ]
            }
        ],
        "globalQualityGates": [
            {
                "gateId": "global-gate",
                "type": "schemaValidation",
                "config": {
                    "schemaUri": "schemas/test.json"
                }
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(manifest_data, f)
        manifest_path = f.name
    
    try:
        # Test loading manifest and converting to model
        manifest = load_manifest(manifest_path)
        
        # Check basic properties
        assert manifest.manifest_version == "1.0.0"
        assert manifest.workflow_id == "test-workflow"
        assert manifest.name == "Test Workflow"
        assert manifest.description == "A test workflow"
        
        # Check stages
        assert len(manifest.stages) == 1
        stage = manifest.stages[0]
        assert stage.stage_id == "stage1"
        assert stage.agent_role == "test-agent"
        assert len(stage.depends_on) == 0
        
        # Check inputs
        assert len(stage.inputs) == 1
        input_artifact = stage.inputs[0]
        assert input_artifact.artifact_type == "video"
        assert input_artifact.artifact_id == "input"
        assert input_artifact.version == "1.0.0"
        assert input_artifact.location == "file:///input.mp4"
        assert input_artifact.producer_stage == ""  # Will be filled during execution
        assert input_artifact.validation_status == "pending"
        
        # Check outputs
        assert len(stage.outputs) == 1
        output_artifact = stage.outputs[0]
        assert output_artifact.artifact_type == "video"
        assert output_artifact.artifact_id == "output"
        assert output_artifact.version == "1.0.0"
        assert output_artifact.location == "file:///output.mp4"
        assert output_artifact.producer_stage == ""  # Will be filled during execution
        assert output_artifact.validation_status == "pending"
        
        # Check quality gates
        assert len(stage.quality_gates) == 0  # No stage-specific quality gates
        
        # Check global quality gates
        assert len(manifest.global_quality_gates) == 1
        global_gate = manifest.global_quality_gates[0]
        assert global_gate["gateId"] == "global-gate"
        assert global_gate["type"] == "schemaValidation"
        
        print("✓ Manifest to model conversion test passed")
        
    finally:
        os.unlink(manifest_path)

def run_all_tests():
    """Run all unit tests."""
    print("Running manifest unit tests...")
    
    test_manifest_load_missing_file()
    test_manifest_load_invalid_json()
    test_manifest_missing_required_fields()
    test_manifest_invalid_field_types()
    test_manifest_stage_validation()
    test_manifest_artifact_reference_validation()
    test_manifest_quality_gate_validation()
    test_manifest_unsupported_version()
    test_manifest_parameter_substitution()
    test_manifest_to_model_conversion()
    
    print("All manifest unit tests passed!")

if __name__ == "__main__":
    run_all_tests()