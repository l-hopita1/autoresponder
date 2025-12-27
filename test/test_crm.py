import sys, os, logging

# Agrego el root del proyecto al path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

# Importo el worker
from python_backend.crm import crmWorker


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    logger = logging.getLogger("TEST_CRM")

    config = {
        "spreadsheet_url": "https://docs.google.com/spreadsheets/d/12E24sqkNvhLOa9_-_DPiceVm9wdFni6Ql_SMQwcTgqE/edit?gid=0#gid=0",
        "worksheet_name": "crm"
    }

    worker = crmWorker(logger)
    worker.init(config)
    worker.handle_crm()


if __name__ == "__main__":
    main()
