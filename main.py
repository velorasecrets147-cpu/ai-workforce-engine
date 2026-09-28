import asyncio
from dotenv import load_dotenv

load_dotenv()

from workflows.client_acquisition import run_client_acquisition


async def main():
    company_name = input("Enter company name: ")

    result = await run_client_acquisition(company_name)

    print("\n=== RESEARCH ===")
    print(result["research"])

    print("\n=== ANALYSIS ===")
    print(result["analysis"])

    print("\n=== DECISION ===")
    print(result["decision"])


if __name__ == "__main__":
    asyncio.run(main())