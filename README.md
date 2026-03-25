# 🌍 ClimateSense - AI Climate Action & Carbon Footprint Reduction Agent

**An Agentic AI system aligned with UN SDG 13: Climate Action**

---

ClimateSense is a production-ready web application that goes beyond simple carbon footprint calculators. It uses **Agentic AI** to reason, prioritize, and guide users toward meaningful climate action.

## 🎯 Core Features

-  **Transparent Carbon Estimation** : Rule-based, explainable footprint calculation
-  **AI-Powered Analysis** : LLM reasoning to identify top emission drivers
-  **Prioritized Recommendations** : Personalized actions ranked by impact vs feasibility
-  **One-Change Challenge** : Weekly, realistic behavior change goals
-  **Climate Advisor Chat** : Context-aware conversational guidance

---

## 🗃️ Architecture

### Modular Agent-Based Design

```
climate_sense/
├── agents/
│   ├── estimator.py          # Rule-based carbon estimation
│   ├── analysis_agent.py     # LLM-based impact analysis
│   ├── recommendation_agent.py  # LLM prioritization
│   ├── challenge_agent.py    # One-Change Challenge generation
│   └── chat_agent.py        # Conversational climate advisor
├── config/
│   └── prompts.py           # Centralized prompt templates
├── utils/
│   └── helpers.py           # Utility functions
└── app.py                   # Flask routes
```
---

## ✔️ Quick Start

### Prerequisites

- Python 3.8+
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd climate_sense
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file and add your GEMINI_API_KEY
   ```

4. **Run the application**
   ```bash
     python app.py
   ```

The app will open in your browser at `http://localhost:8501`
---

## 🪴 Usage Flow

1. **Introduction**: Learn about ClimateSense and SDG 13
2. **Lifestyle Input**: Fill out the questionnaire about your lifestyle
3. **Footprint Results**: View your carbon footprint breakdown
4. **AI Analysis**: Get AI-powered insights on your top emission drivers
5. **Recommendations**: Receive prioritized, personalized action recommendations
6. **One-Change Challenge**: Accept a weekly challenge to reduce your footprint
7. **Climate Advisor Chat**: Ask follow-up questions and get guidance

---

## ⚙️ Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

### Customization

- **Scoring Weights**: Modify `agents/estimator.py` to adjust carbon scoring
- **Prompts**: Edit `config/prompts.py` to customize AI behavior
- **UI**: Modify `app.py` to change the user interface

---

## 📑 Design Principles

### Agentic AI

ClimateSense demonstrates **Agentic AI** through:

- **Reasoning**: LLM analyzes footprint data and explains why factors matter
- **Prioritization**: AI ranks actions by impact vs feasibility
- **Decision Support**: Provides personalized guidance, not generic advice

### Ethical AI

- ✅ Encouraging, non-judgmental language
- ✅ Realistic, achievable recommendations
- ✅ Privacy-first (session-based storage)
- ✅ Clear disclaimers about estimates
- ✅ No fear-based messaging

---

##  Technical Stack

- **Frontend**: (HTML/CSS)
- **Backend**: Python 3.8+
- **LLM**: Google Gemini API
- **Storage**: Session-based (Streamlit session_state)
- **Deployment**: Hugging Faces

---

## 🤝 Contributing

This is a portfolio-ready project demonstrating:
- Agentic AI principles
- Responsible AI practices
- Production-ready code structure
- UN SDG alignment

---

## 📝 License

This project is built for educational and portfolio purposes.

---

## 📜 Acknowledgments

- Inspired by Kaggle "Individual Carbon Footprint Calculation" dataset
- Aligned with United Nations Sustainable Development Goal (UN SDG 13: Climate Action)
- Built with ethical AI principles

---

