# How Strong is Your Weakest Link?

**Live demo: weakestlink.streamlit.app**

An interactive Streamlit web app that teaches people how data breaches put passwords at risk. Users can check whether a password has appeared in known breaches, see how it compares to a sample of leaked passwords, and read short, sourced explanations of why password habits matter.

## Purpose

People are often called the "weakest link" in security because they choose predictable passwords and reuse them across sites. This app makes that idea concrete in three ways:

1. **Breach check.** The user enters a password (or picks an example) and the app reports how many times it has appeared in known data breaches.
2. **Visualizing leaked passwords.** Two charts show how leaked passwords are distributed by length and by character mix, and highlight where the user's password falls.
3. **Awareness.** Four tabs explain what a breach is, why breaches matter, why a password still matters after a breach, and what the Federal Trade Commission (FTC) recommends. Sources are listed in the app.

Character mix is grouped into five categories: digits only, lowercase letters only, letters only (upper or mixed case), letters and digits, and includes symbols.

## Privacy

The app is designed so the password never leaves the user's session in readable form:

- The password is hashed with SHA-1 (the format the Pwned Passwords service requires), and **only the first 5 characters of the hash** are sent to the API. The service returns every hash sharing that prefix, and the match is made locally.
- The input box is cleared as soon as the form is submitted, and only derived facts (length, character category, breach count) are kept in session state.
- Even so, **do not enter a password you currently use.** Try one that is similar in style, or use one of the built-in examples (`password123`, `qwerty`, `Summer2024!`).

## Dataset Used

The app uses one data source:

1. **Pwned Passwords API (live lookup).** Breach counts come from the [Pwned Passwords](https://haveibeenpwned.com/Passwords) range API by Have I Been Pwned (`https://api.pwnedpasswords.com/range/`). An internet connection is required for the breach check.

2. **Leaked-password sample (`data/leaked_summary.csv`).** The charts and insights are built from a trimmed sample of the previously mentioned public leaked-password dataset (Pwned Passwords)

   Each row is a count of passwords, so the CSV holds aggregate statistics rather than the passwords themselves. If the file is missing, the app still runs but shows a warning in place of the charts.

   About the sample: it has 59 rows covering **6,845 leaked passwords** with lengths from 3 to 20 characters. About 85% are 8 characters or shorter, and only about 0.3% (23 passwords) contain a symbol. These are the figures the app's Insights section reports.

The explainer tabs also draw on published research and guidance (Bonneau 2012; Das et al. 2014; Thomas et al. 2017; FTC 2024), listed under **Sources** in the app.

## Requirements

- Python 3.10 or newer
- A newer version of Streamlit
- An internet connection

Python packages (from `requirements.txt`): `streamlit`, `pandas`, `plotly`, `requests`.

## User instructions

### Use the hosted app

Open weakestlink.streamlit.app in any browser. No installation is needed. Then skip to Using the app below.

### Run the app locally

1. Clone the repository:

   ```bash
   git clone https://github.com/sabrinamalvarez/password-checker.git
   cd password-checker
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the app:

   ```bash
   streamlit run app.py
   ```

4. Streamlit prints a local address (usually `http://localhost:8501`). Open it in your browser.

### Using the app

1. **Read the background.** Browse the four tabs under *About data breaches* for context.
2. **Check a password.**
   - Type a password into the *Password to check* box, **or** choose one from the *Or try an example* dropdown.
   - Click **Check password**. If you type a password and also pick an example, the typed password is used.
   - If both are empty, the app asks you to enter or pick one first.
3. **Read your result.**
   - A red message means the password appears in known breaches and shows how many times. Do not use it anywhere.
   - A green message means it was not found. This does not mean it is strong, because long, unique passwords are what protect you.
   - Three metrics show the breach count, the password's length, and its character mix.
   - If the service cannot be reached, you will see a warning and the breach count will show as *Unknown*. The length and character mix are still reported.
4. **Compare with leaked passwords.** Scroll to *Visualizing Data Leaks*. Your password's length bar and character-mix slice are highlighted in purple.
5. **Check another password.** The input box clears after each check; submit again to replace the result.

