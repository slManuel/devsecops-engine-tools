from datetime import datetime
import pytest
from unittest.mock import patch, MagicMock
from devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.docker.docker_images import (
    DockerImages,
)


@pytest.fixture
def mock_docker_client():
    with patch("docker.from_env") as mock:
        yield mock

@pytest.fixture
def base_image_labels():
    return ["x86.image.name", "image.base.ref.name", "source-image", "source_images"]

def test_list_images(mock_docker_client):
    # Arrange
    docker_images = DockerImages()
    image_to_scan = "test_image:latest"

    mock_client = MagicMock()
    mock_docker_client.return_value = mock_client

    mock_image1 = MagicMock()
    mock_image1.tags = ["non_matching_image:latest", "other_tag:v1"]
    mock_image1.id = "non_matching_id_1"
    mock_image1.attrs = {"Created": "2023-08-01T10:00:00.000Z"}

    mock_image2 = MagicMock()
    mock_image2.tags = ["another_non_matching_image:latest", "different_tag:v2"]
    mock_image2.id = "non_matching_id_2"
    mock_image2.attrs = {"Created": "2023-08-01T11:00:00.000Z"}

    mock_image3 = MagicMock()
    mock_image3.tags = ["some_other_image:v1", image_to_scan, "another_tag:v2"]
    mock_image3.id = "test_id"
    mock_image3.attrs = {"Created": "2023-08-02T12:34:56.789Z"}

    mock_client.images.list.return_value = [mock_image1, mock_image2, mock_image3]

    # Act
    result = docker_images.list_images(image_to_scan)

    # Assert
    assert result == mock_image3
    assert result.id == "test_id"
    assert image_to_scan in result.tags
    assert result.attrs["Created"] == "2023-08-02T12:34:56.789Z"
    mock_docker_client.assert_called_once()
    mock_client.images.list.assert_called_once()


def test_list_images_no_matching_image(mock_docker_client):
   
    docker_images = DockerImages()
    image_to_scan = "non_existent_image:latest"

    mock_client = MagicMock()
    mock_docker_client.return_value = mock_client

    mock_image1 = MagicMock()
    mock_image1.tags = ["some_image:latest"]
    mock_image2 = MagicMock()
    mock_image2.tags = ["another_image:latest"]

    mock_client.images.list.return_value = [mock_image1, mock_image2]


    result = docker_images.list_images(image_to_scan)


    assert result is None
    mock_client.images.list.assert_called_once()


def test_list_images_exception(mock_docker_client):

    docker_images = DockerImages()
    image_to_scan = "test_image:latest"

    mock_client = MagicMock()
    mock_docker_client.side_effect = Exception("Docker not running")


    result = docker_images.list_images(image_to_scan)


    assert result is None
    mock_docker_client.assert_called_once()

def test_get_base_image_source_label(mock_docker_client, base_image_labels):
    docker_images = DockerImages()
    matching_image = MagicMock()
    matching_image.id = "image_id"
    
    mock_client = MagicMock()
    mock_docker_client.return_value = mock_client
    mock_client.api.inspect_image.return_value = {
        "Config": {"Labels": {"x86.image.name": "source_image:1.0"}},
    }
    
    result, is_distroless = docker_images.get_base_image(matching_image, base_image_labels)
    assert result == ["source_image:1.0"]
    assert not is_distroless
    mock_client.api.inspect_image.assert_called_once_with("image_id")

def test_get_base_image_no_base_image(mock_docker_client, base_image_labels):
    docker_images = DockerImages()
    matching_image = MagicMock()
    matching_image.id = "image_id"
    
    mock_client = MagicMock()
    mock_docker_client.return_value = mock_client
    mock_client.api.inspect_image.return_value = {"Config": {"Labels": {}}}
    
    result, is_distroless = docker_images.get_base_image(matching_image, base_image_labels)
    assert result is None
    assert not is_distroless
    mock_client.api.inspect_image.assert_called_once_with("image_id")

def test_get_base_image_exception(mock_docker_client, base_image_labels):
    docker_images = DockerImages()
    matching_image = MagicMock()
    matching_image.id = "image_id"
    
    mock_client.api.inspect_image.side_effect = Exception("Inspection failed")
    
    result, is_distroless = docker_images.get_base_image(matching_image, base_image_labels)
    assert result is None
    assert not is_distroless
    mock_client.api.inspect_image.assert_called_once_with("image_id")

def test_validate_base_image_date_with_baseline_date(mock_docker_client, base_image_labels):
    docker_images = DockerImages()
    matching_image = MagicMock()
    matching_image.id = "image_id"
    referenced_date = "20230801"
    
    mock_client = MagicMock()
    mock_docker_client.return_value = mock_client
    mock_client.api.inspect_image.return_value = {
        "Config": {"Labels": {"x86.baseline.date": "20230802"}}
    }
    
    result = docker_images.validate_base_image_date(matching_image, referenced_date, base_image_labels)
    assert result is True
    mock_client.api.inspect_image.assert_called_once_with("image_id")

def test_validate_base_image_date_without_baseline_date(mock_docker_client, base_image_labels):
    docker_images = DockerImages()
    matching_image = MagicMock()
    matching_image.id = "image_id"
    referenced_date = "20230801"
    
    mock_client = MagicMock()
    mock_docker_client.return_value = mock_client
    mock_client.api.inspect_image.return_value = {
        "Config": {"Labels": {"source_images": "base_image_20230802"}}
    }
    
    with patch.object(docker_images, 'extract_date_from_image', return_value=datetime.strptime("20230802", "%Y%m%d")):
        result = docker_images.validate_base_image_date(matching_image, referenced_date, base_image_labels)
    
    assert result is True
    mock_client.api.inspect_image.assert_called_once_with("image_id")

def test_validate_base_image_date_older_than_referenced_date(mock_docker_client, base_image_labels):
    docker_images = DockerImages()
    matching_image = MagicMock()
    matching_image.id = "image_id"
    referenced_date = "20230802"
    
    mock_client = MagicMock()
    mock_docker_client.return_value = mock_client
    mock_client.api.inspect_image.return_value = {
        "Config": {"Labels": {"x86.baseline.date": "20230801"}}
    }
    
    with pytest.raises(ValueError, match="Compliance issue:"):
        docker_images.validate_base_image_date(matching_image, referenced_date, base_image_labels)
    
    mock_client.api.inspect_image.assert_called_once_with("image_id")
    
def test_validate_black_list_base_image_valid_not_blacklisted():
    docker_images = DockerImages()
    base_image = "my_image:latest"
    black_list = ["forbidden", "banned"]
    result = docker_images.validate_black_list_base_image(base_image, black_list)
    assert result is True

def test_validate_black_list_base_image_valid_blacklisted():
    docker_images = DockerImages()
    base_image = "forbidden_image:latest"
    black_list = ["forbidden", "banned"]
    with pytest.raises(ValueError, match="Compliance issue: the image: forbidden_image:latest is blacklisted for forbidden"):
        docker_images.validate_black_list_base_image(base_image, black_list)

def test_validate_black_list_base_image_blacklisted_partial_match():
    docker_images = DockerImages()
    base_image = "my_image:banned"
    black_list = ["forbidden", "banned"]
    with pytest.raises(ValueError, match="Compliance issue: the image: my_image:banned is blacklisted for banned"):
        docker_images.validate_black_list_base_image(base_image, black_list)

def test_validate_black_list_base_image_invalid_base_image_type():
    docker_images = DockerImages()
    base_image = 12345  # Not a string
    black_list = ["forbidden"]
    result = docker_images.validate_black_list_base_image(base_image, black_list)
    assert result is False

def test_validate_black_list_base_image_invalid_black_list_type():
    docker_images = DockerImages()
    base_image = "my_image:latest"
    black_list = "not_a_list"  # Not a list
    result = docker_images.validate_black_list_base_image(base_image, black_list)
    assert result is False

def test_validate_black_list_base_image_empty_black_list():
    docker_images = DockerImages()
    base_image = "my_image:latest"
    black_list = []
    result = docker_images.validate_black_list_base_image(base_image, black_list)
    assert result is True



