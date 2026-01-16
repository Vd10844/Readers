import asyncio
from pathlib import Path
from services.extract import extract_plot_data


async def run():
    file_path = Path(
        r"D:\10844\Q4\Jan\Week_02\LLM\sample\image.png"
    )

    result = await extract_plot_data(file_path)
    print("\n=== EXTRACTION RESULT ===\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(run())
