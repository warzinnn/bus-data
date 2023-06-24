class BusCompany:
    def __init__(
        self, code_area_operation, company_reference_code: int, company_name: str
    ) -> None:
        self.code_area_operation = code_area_operation
        self.company_reference_code = company_reference_code
        self.company_name = company_name
