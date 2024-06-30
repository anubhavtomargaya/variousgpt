from pathlib import Path

root = Path(__file__).parent.resolve()
PDF_DIR = Path(root,'pdf')

if __name__=='__main__':
    print(PDF_DIR)