import datetime

class Document:
    # Document with title, author, date created, date last modified, description, and content
    def __init__(self, title="", author="", date_created=datetime.datetime.now(), date_modified="", description="", content="", file_name=""):
        self.title = title
        self.author = author
        self.date_created = date_created
        self.date_modified = date_modified
        self.description = description
        self.content = content
        self.file_name = file_name
    
    def __str__(self):
        return f"Title: {self.title}\nAuthor: {self.author}\nDate Created: {self.date_created}\nDate Modified: {self.date_modified}\nDescription: {self.description}\nContent: {self.content}"
    
    def toString(self):
        return f"Title: {self.title}\nAuthor: {self.author}\nDate Created: {self.date_created}\nDate Modified: {self.date_modified}\nDescription: {self.description}\nContent: {self.content}"

    def updateModified(self):
        # Update the date modified to the current date and time
        self.date_modified = datetime.datetime.now()

    def save(self, name):
        # Save the text in the text box to a file
        if name:
            with open(name, 'w') as file:
                file.write(self.toString())
        else:
            if self.file_name:
                with open(self.file_name, 'w') as file:
                    file.write(self.toString())
            else:
                raise ValueError("No file name provided")

    def load(self, name):
        # Load text from file in, including title, author, date created, date modified, description, and content
        with open(name, 'r') as file:
            text = file.read()
            lines = text.split("\n")
            if len(lines) < 6:
                self.content = text
                return
            self.title = lines[0].split(": ")[1].strip()
            self.author = lines[1].split(": ")[1].strip()
            if lines[2].split(": ")[1].strip():
                self.date_created = datetime.datetime.strptime(lines[2].split(": ")[1].strip(), '%Y-%m-%d %H:%M:%S.%f')
            if lines[3].split(": ")[1].strip():
                self.date_modified = datetime.datetime.strptime(lines[3].split(": ")[1].strip(), '%Y-%m-%d %H:%M:%S.%f')
            self.description = lines[4].split(": ")[1].strip()
            self.content = lines[5].split(": ")[1].strip()
            self.file_name = name