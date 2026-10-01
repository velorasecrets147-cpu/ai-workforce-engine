import asyncio
import json

from dotenv import load_dotenv

load_dotenv()

from workflows.client_acquisition import run_client_acquisition


async def main():
    company_name = input("Enter company name: ").strip()

    if not company_name:
        print("Company name cannot be empty.")
        return

    result = await run_client_acquisition(company_name)

    print("\n=== WORKFLOW ===")
    print(
        json.dumps(
            result["workflow_run"].model_dump(),
            indent=2,
            ensure_ascii=False,
        )
    )

    print("\n=== RESEARCH ===")
    print(
        json.dumps(
            result["research"].model_dump(),
            indent=2,
            ensure_ascii=False,
        )
    )

    print("\n=== ANALYSIS ===")
    print(
        json.dumps(
            result["analysis"].model_dump(),
            indent=2,
            ensure_ascii=False,
        )
    )

    print("\n=== DECISION ===")
    print(
        json.dumps(
            result["decision"].model_dump(),
            indent=2,
            ensure_ascii=False,
        )
    )

    print("\n=== EVALUATION ===")
    print(
        json.dumps(
            result["evaluation"].model_dump(),
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())