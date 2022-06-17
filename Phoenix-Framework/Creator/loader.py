"""Create Loaders to download the stager and execute it."""
from Utils import curr, conn


def create_loader(name, language, stager_id):
    """
    Create a Loader

    :param language: The language of the loader
    :param stager_id: The ID of the stager
    """
    # Check if stager exists
    curr.execute("SELECT * FROM Stagers WHERE Id = ?", (stager_id,))
    stager = curr.fetchone()
    if not stager:
        raise Exception(f"Stager with ID {stager_id} does not exist")

    # Check if language is valid
    if language not in ["python",
                        "powershell",
                        "php",
                        "java",
                        "batch",
                        "php",
                        "javascript",
                        "shell"]:
        raise Exception(f"Language {language} is not supported")

    # Save Loader
    curr.execute("INSERT INTO Loaders (Name, Language, StagerId) VALUES (?, ?, ?)",
                 (name, language, stager_id))
    conn.commit()
    return f"Loader {name} created"


def get_loader(loader_id):
    """
    Get a Loader

    :param loader_id: The ID of the Loader
    """
    # Check if Loader exists
    curr.execute("SELECT * FROM Loaders WHERE Id = ?", (loader_id,))
    loader = curr.fetchone()
    if not loader:
        raise Exception(f"Loader with ID {loader_id} does not exist")
