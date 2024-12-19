# Parents Copilot -Child Development Assistant 👶

A Streamlit-based application that helps parents help their children's development and provides personalized stories and Montessori activities.

## Features 🌟

- **Child Registration**: Easily register and manage your children's information
- **Age Tracking**: Automatically calculates and displays ages in the most appropriate format (days, months, or years)
- **Personalized Stories**: Generates age-appropriate stories tailored to each child
- **Montessori Activities**: Suggests educational activities based on the child's developmental stage
- **User-Friendly Interface**: Clean and intuitive design with emoji-enhanced interactions

## Technology Stack 🛠️

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: Firebase Database
- **AI Integration**: OpenAI GPT for content generation
- **Dependencies Management**: Requirements.txt

## Prerequisites 📋

- Python 3.8+
- OpenAI API key
- Firebase credentials

## Installation 🔧

1. Clone the repository
```bash
git clone [repository-url]
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure your environment variables in `.streamlit/secrets.toml`:
```toml
[openai]
api_key = "your-openai-api-key"

[firebase]
credencials = {
  # Your Firebase credentials here
}
```

4. Run the application
```bash
streamlit run app.py
```

## Project Structure 📁

```
├── app.py                 # Main application file
├── child_assistant.py     # Core assistant functionality
├── firebase_manager.py    # Firebase database operations
├── prompts.yaml          # AI prompt templates
├── pages/                # Streamlit pages
│   ├── 1_📚_cuenta_cuentos.py    # Story generation page
│   └── 2_🎯_Actividades_diarias.py   # Activities page
└── components/           # Reusable components
    └── child_selector.py # Child selection component
```

## Features in Detail 🔍

### Story Generation
- Creates personalized stories based on the child's name and age
- Adapts content complexity to developmental stage
- Uses engaging and age-appropriate language

### Montessori Activities
- Suggests activities aligned with Montessori principles
- Tailored to the child's developmental needs
- Includes materials and instructions

### Child Management
- Track multiple children
- Automatic age calculation
- Easy-to-use registration form

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- OpenAI for providing the GPT API
- Streamlit for the amazing web framework
- Firebase for reliable data storage
