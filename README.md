# Setup Instructions

## 1. Install Dependencies

```bash
brew install tesseract poppler
pip install -r requirements.txt
```

## 2. Set Environment Variables

The only thing really needed is the OpenAI API key.

Update the FORM_URL to have it adapt to the form you are trying to fill out.

```bash
cp fastapi/.env.example fastapi/.env
```

## 3. Run the Application

Run the script to start the application.
```bash
./run-dev.sh
```