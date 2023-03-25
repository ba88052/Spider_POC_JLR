# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from google.cloud import bigquery
import time
import logging


class BigQueryPipeline:

    def __init__(self, project_id, dataset_id, table_id):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            project_id=crawler.settings.get('GCP_PROJECT_ID'),
            dataset_id=crawler.settings.get('BQ_DATASET_ID'),
            table_id=crawler.settings.get('BQ_TABLE_ID')
        )

    def open_spider(self, spider):
        self.client = bigquery.Client(project=self.project_id)

        # Create dataset if not exists
        dataset_ref = self.client.dataset(self.dataset_id)
        try:
            dataset = bigquery.Dataset(dataset_ref)
            self.client.create_dataset(dataset)
            logging.info(f"Create dataset {dataset_ref}")
        except Exception as e:
            self.client.get_dataset(dataset_ref)  
            logging.info(f"Dataset {dataset_ref} already exist")

        # Create table if not exists
        self.table_ref = dataset_ref.table(spider.bq_table_name)

        if spider.bq_table_name.startswith('judgement_link_'):
            try:
                schema = [
                    bigquery.SchemaField("START_DATE", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("END_DATE", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("JLR_LINK", "STRING", mode="NULLABLE")
                ]
                table = bigquery.Table(self.table_ref, schema = schema)
                self.client.create_table(table)
                logging.info(f"Create table {self.table_ref}")
            # 如果x以'tax_num_'为前缀，则执行以下代码
            except Exception as e:
                time.sleep(5)
                logging.info(f"Table {self.table_ref} already exist")

        elif spider.bq_table_name.startswith('judgement_info_'):
            try:
                schema = [
                    bigquery.SchemaField("DECISION_NAME", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("LEGAL_RELATIONSHIP", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("JUDGMENT_LEVEL", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("TYPE_OF_CASE", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("TRIAL_COURT", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("APPLICATION_OF_PRECEDENT", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("CORRECTIONS", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("INFORMATION_ABOUT_THE_CASE", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("TOTAL_NUMBER_OF_VOTES_VOTED_AS_THE_SOURCE_OF_CASE_LAW_DEVELOPMENT", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("PDF_TEXT", "STRING", mode="NULLABLE"),
                ]
                table = bigquery.Table(self.table_ref, schema = schema)
                self.client.create_table(table)
                logging.info(f"Create table {self.table_ref}")
            except Exception as e:
                time.sleep(5)
                logging.info(f"Table {self.table_ref} already exist")
                

            
            
    def process_item(self, item, spider):
        item_data = dict(item)
        errors = self.client.insert_rows_json(self.table_ref, [item_data])
        if errors:
            raise Exception(f"Errors while streaming data to BigQuery: {errors}")

        return item

class SpiderPocGdtPipeline:
    def process_item(self, item, spider):
        return item
