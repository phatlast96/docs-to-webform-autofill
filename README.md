# Setup Instructions

## 1. Install Dependencies

```bash
brew install tesseract poppler
pip install -r requirements.txt
```

## 2. Set Environment Variables

The only thing really needed is the OpenAI API key.
```bash
cp fastapi/.env.example fastapi/.env
```

## 3. Run the Application

Run the script to start the application.
```bash
./run-dev.sh
```