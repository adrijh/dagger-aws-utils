from typing import Any

from f_with_dockerfile.__main__ import main


def lambda_handler(event: dict[str, Any], context: Any) -> None:
    main()

