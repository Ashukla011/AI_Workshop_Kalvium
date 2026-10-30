# Day 1 Workshop | Python Web App

A beginner-friendly web application developed with **Python and Streamlit** as part of the first-day workshop. The project focuses on building an interactive web interface and understanding the basic workflow for local development, dependency management, and Git-based version control.

## 🧰 Getting Started

Follow the instructions below to set up the project on your computer.

### 1. Download the Repository

Clone the project and move into its directory:

```bash
https://github.com/Ashukla011/AI_Workshop_Kalvium
cd "Day_1"
```

### 2. Enable the Virtual Environment

Activate your Python environment according to your operating system.

**Windows (PowerShell)**

```powershell
.env\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .env/bin/activate
```

### 3. Install the Required Package

Install Streamlit to run the web application:

```bash
pip install streamlit
```

## 🚀 Start the Application

Once the environment and dependency are ready, launch the app with:

```bash
streamlit run app.py
```

Streamlit will start a local development server and provide a URL where you can access the application in your browser.

## 📂 Project Structure

| File or Folder | Purpose |
|---|---|
| `app.py` | Main Python script containing the Streamlit interface and application logic. |
| `.gitignore` | Specifies local files and folders Git should leave untracked, such as virtual environments and editor-specific settings. |
| `.env/` | Local virtual environment used to isolate project dependencies. |

## 🎯 Workshop Highlights

During this session, the project covered the following practical tasks:

- Created an isolated Python environment for project development.
- Organized the workspace and source files using Visual Studio Code.
- Built an interactive web interface with Streamlit components.
- Initialized a Git repository to track changes in the source code.
- Connected the local project to a remote GitHub repository.

## 🧪 Technologies Used

- **Python** — application development
- **Streamlit** — interactive web interface
- **Git** — source code version control
- **GitHub** — remote repository hosting
- **Visual Studio Code** — development environment

## 📝 Notes

- Run the commands from the appropriate project directory.
- Activate the virtual environment before installing packages or starting the app.
- Ensure that `app.py` exists in the directory from which you run Streamlit.
- If the repository uses additional Python packages, install them as well. A `requirements.txt` file can be used to document the complete dependency list.

---

*Built as a hands-on learning project during the Day 1 workshop.*
