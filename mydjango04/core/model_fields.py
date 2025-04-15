import ipaddress
from typing import Union, Optional
from django.db import models
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models import Expression

from django.core.exceptions import ValidationError

class BooleanYNField(models.BooleanField):
    """Y/N 형태로 데이터베이스에 저장되는 Boolean 필드를 정의"""
    true_value = "Y"
    false_value = "N"
    
    # BooleanField 디폴트 에러 메시지 재정의
    default_error_messages = {
        # null=False 일 때의 값 오류 메시지
        "invalid": (
            f"“%(value)s” 값은 True/False 값이어야 하며 "
            f"'{true_value}'/'{false_value}' 문자열도 지원합니다."
        ),
        # null=True 일 때의 값 오류 메시지
        "invalid_nullable": (
            f"“%(value)s” 값은 None이거나 True/False 값이어야 하며 "
            f"'{true_value}'/'{false_value}' 문자열도 지원합니다."
        ),
    }
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 1)
        super().__init__(*args, **kwargs)
    
    def get_internal_type(self):
        return "CharField"
    
    def to_python(self, value:Union[str, bool]) -> Optional[bool]:
        """데이터베이스 값, 폼 입력, 쿼리셋 조회값을 True/False/None 값으로 변환합니다."""
        if self.null and value in self.empty_values:
            return None
        
        # Y/N 문자열만 직접 처리하고,
        if value == self.true_value : return True
        elif value == self.false_value  : return False
        
        # 나머지 값에 대한 변환은 부모인 models.BooleanField에게 넘깁니다.
        return super().to_python(value)
    
    def from_db_value(self, value:Optional[str], expression: Expression, connection:BaseDatabaseWrapper) -> Optional[bool]:
        """데이터베이스에서 읽어온 값을 True/False/None 값으로 변환합니다."""
        return self.to_python(value)
    
    def get_prep_value(self, value: Union[bool, str]) -> Optional[str]:
        """SQL 쿼리가 작성될 때 호출됩니다. Y/N/True/False 값을 데이터베이스에 저장할 문자열 Y/N이나 None으로 변환합니다."""
        prep_value: Optional[bool] = super().get_prep_value(value)  # 내부에서 to_python을 호출하여 값을 변환
        if prep_value is None:
            return None
        
        return self.true_value if prep_value else self.false_value

class IPv4AddressIntegerField(models.CharField):
    default_error_messages = {
        "invalid": "“%(value)s” 값은 IPv4 주소나 정수여야 합니다.",
        "invalid_nullable": "“%(value)s” 값은 None이거나 IPv4 주소나 정수여야 합니다.",
    }
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 15)
        super().__init__(*args, **kwargs)
    
    def get_internal_type(self):
        return "PositiveIntegerField"
    
    def db_type(self, connection):
        if connection.vendor == "postgresql":
            return "bigint"
        elif connection.vendor == "oracle":
            return "number(19)"
        
        return super().db_type(connection)
    
    def to_python(self, value: Union[str, int]) -> Optional[str]:
        # 만약 이 필드가 null을 허용하고, 현재 값이 비어 있는 값 중 하나라면.
        if self.null and value in self.empty_values:
            return None
        
        # 만약 value가 문자열이고 그 문자열이 숫자라면
        if isinstance(value, str) and value.isdigit():
            value = int(value)
        
        try:
            return str(ipaddress.IPv4Address(value))  # 문자열 아이피로 변환
        except(ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            raise ValidationError(
                self.default_error_messages["invalid_nullable" if self.null else "invalid"],
                code="invalid", params={"value": value}
            )
    
    def from_db_value(self, value: Optional[int], expression, connection) -> str:
        """데이터베이스에서 읽어온 값을 문자열 아이피나 None으로 변환합니다."""
        return self.to_python(value)
    
    def get_prep_value(self, value: Union[str, int]) -> Optional[int]:
        """SQL 쿼리가 작성될 때 호출됩니다. 정수/문자열 아이피를 데이터베이스에 저장할 정수나 None으로 변환합니다."""
        prep_value: Optional[str] = super().get_prep_value(value)
        
        if prep_value is None:
            return None
        
        return int(ipaddress.IPv4Address(prep_value))