from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from models import EmailEntry
from verifier_app.tasks import verify_address


class Processor():
    database = None
    mx_list = None
    use_tor = None
    rotation_num = 0

    def __init__(self, mx_list, use_tor, rotation_num):
        self.database = create_engine('sqlite:///database.db', poolclass=QueuePool)
        self.mx_list = mx_list
        self.use_tor = use_tor
        self.rotation_num = rotation_num

    def start_processing(self):
        Session = sessionmaker(bind=self.database)
        session = Session()
        entries = session.query(EmailEntry).filter(EmailEntry.processed == False)
        session.close()

        for entry in entries:
            verify_address.delay(entry.id, self.mx_list, self.use_tor, self.rotation_num)
