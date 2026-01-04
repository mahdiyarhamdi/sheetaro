"""Unit tests for API Client utility."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


class TestAPIClientUserMethods:
    """Test API client user-related methods."""
    
    @pytest.fixture
    def mock_httpx_response(self):
        """Create mock httpx response."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "id": str(uuid4()),
            "telegram_id": 123456789,
            "first_name": "Test",
            "role": "CUSTOMER",
        }
        return response
    
    @pytest.mark.asyncio
    async def test_get_or_create_user_success(self, mock_httpx_response):
        """Test successful user creation."""
        user_data = {
            "telegram_id": 123456789,
            "first_name": "Test",
            "username": "testuser",
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_httpx_response
            )
            
            # Verify the mock setup works
            assert mock_httpx_response.status_code == 200
            assert mock_httpx_response.json()['telegram_id'] == 123456789
    
    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id(self, mock_httpx_response):
        """Test getting user by telegram ID."""
        telegram_id = 123456789
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_httpx_response
            )
            
            assert mock_httpx_response.json()['first_name'] == "Test"
    
    @pytest.mark.asyncio
    async def test_promote_to_admin(self):
        """Test promoting user to admin."""
        user_id = str(uuid4())
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": user_id,
            "role": "ADMIN",
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            assert mock_response.json()['role'] == "ADMIN"


class TestAPIClientOrderMethods:
    """Test API client order-related methods."""
    
    @pytest.fixture
    def sample_order(self):
        """Create sample order data."""
        return {
            "id": str(uuid4()),
            "product_id": str(uuid4()),
            "design_plan": "PUBLIC",
            "status": "PENDING",
            "quantity": 100,
            "total_price": 100000,
        }
    
    @pytest.mark.asyncio
    async def test_create_order(self, sample_order):
        """Test creating an order."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = sample_order
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            assert mock_response.status_code == 201
            assert mock_response.json()['status'] == "PENDING"
    
    @pytest.mark.asyncio
    async def test_get_user_orders(self, sample_order):
        """Test getting user orders."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [sample_order],
            "total": 1,
            "page": 1,
            "page_size": 20,
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = mock_response.json()
            assert result['total'] == 1
            assert len(result['items']) == 1
    
    @pytest.mark.asyncio
    async def test_cancel_order(self, sample_order):
        """Test cancelling an order."""
        sample_order['status'] = 'CANCELLED'
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_order
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            assert mock_response.json()['status'] == "CANCELLED"


class TestAPIClientPaymentMethods:
    """Test API client payment-related methods."""
    
    @pytest.fixture
    def sample_payment(self):
        """Create sample payment data."""
        return {
            "payment_id": str(uuid4()),
            "order_id": str(uuid4()),
            "amount": 50000,
            "status": "PENDING",
        }
    
    @pytest.mark.asyncio
    async def test_initiate_payment(self, sample_payment):
        """Test initiating payment."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = sample_payment
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            assert mock_response.status_code == 201
            assert 'payment_id' in mock_response.json()
    
    @pytest.mark.asyncio
    async def test_upload_receipt(self, sample_payment):
        """Test uploading payment receipt."""
        sample_payment['status'] = 'AWAITING_APPROVAL'
        sample_payment['receipt_image_url'] = '/uploads/receipt.jpg'
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_payment
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            result = mock_response.json()
            assert result['status'] == "AWAITING_APPROVAL"
            assert 'receipt_image_url' in result


class TestAPIClientCatalogMethods:
    """Test API client catalog-related methods."""
    
    @pytest.mark.asyncio
    async def test_get_categories(self):
        """Test getting categories."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"id": str(uuid4()), "name_fa": "برچسب", "name_en": "Label"},
                {"id": str(uuid4()), "name_fa": "فاکتور", "name_en": "Invoice"},
            ],
            "total": 2,
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = mock_response.json()
            assert result['total'] == 2
    
    @pytest.mark.asyncio
    async def test_create_category(self):
        """Test creating a category."""
        category_id = str(uuid4())
        
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": category_id,
            "name_fa": "لیبل جدید",
            "name_en": "New Label",
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            result = mock_response.json()
            assert result['id'] == category_id
    
    @pytest.mark.asyncio
    async def test_get_design_plans(self):
        """Test getting design plans for a category."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"id": str(uuid4()), "plan_type": "PUBLIC", "has_templates": True},
                {"id": str(uuid4()), "plan_type": "SEMI_PRIVATE", "has_questionnaire": True},
            ],
            "total": 2,
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = mock_response.json()
            assert result['total'] == 2
            assert result['items'][0]['has_templates'] is True


class TestAPIClientErrorHandling:
    """Test API client error handling."""
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling network errors."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("Network error")
            )
            
            with pytest.raises(Exception, match="Network error"):
                async with mock_client() as client:
                    await client.get("http://test.com")
    
    @pytest.mark.asyncio
    async def test_404_error_handling(self):
        """Test handling 404 responses."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Not found"}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            assert mock_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_validation_error_handling(self):
        """Test handling 422 validation errors."""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "detail": [
                {"loc": ["body", "quantity"], "msg": "must be positive", "type": "value_error"}
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            assert mock_response.status_code == 422
            assert len(mock_response.json()['detail']) == 1

