from src.etl_service.transform import transform_data, save_to_staging
from src.etl_service.mart import mart_pipeline


def run_etl_pipeline():
    print("Transform aşaması başlıyor...")
    assets = transform_data()
    print(f"{len(assets)} varlık transform edildi.")

    save_to_staging(assets)
    print("Veriler staging tablosuna kaydedildi.")

    print("Mart aşaması başlıyor...")
    mart_pipeline()
    print("ETL pipeline tamamlandı.")


if __name__ == "__main__":
    run_etl_pipeline()
