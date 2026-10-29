import hashlib
import string
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


st.set_page_config(page_title="Has Your Password Been Pwned?", layout="wide")

SUMMARY_PATH = Path(__file__).parent / "data" / "leaked_summary.csv"
RANGE_URL = "https://api.pwnedpasswords.com/range/"
USER_AGENT = "password-checker-class-project"

EXAMPLES = ["password123", "qwerty", "Summer2024!"]

GREY, PURPLE = "#8c93a0", "#952fd0ff"

# -------------- Password Helpers --------------
# These functions are helpers for the password search. 
# They help categorize the data so it can be compared with the API sample

LOWER, UPPER, DIGITS = set(string.ascii_lowercase), set(string.ascii_uppercase), set(string.digits)
LENGTH_CAP = 20  # lengths above this are grouped as "20+"
CATEGORIES = [
    "Digits only",
    "Lowercase letters only",
    "Letters only (upper or mixed case)",
    "Letters and digits",
    "Includes symbols",
]

# Any of these return true if they are found in the USER's password.
def char_classes(pw: str) -> dict:
    return {
        "lower": any(c in LOWER for c in pw),
        "upper": any(c in UPPER for c in pw),
        "digit": any(c in DIGITS for c in pw),
        "symbol": any(c not in LOWER and c not in UPPER and c not in DIGITS for c in pw),
    }

# This puts the password into different categories in priority order.
def category(pw: str) -> str:
    c = char_classes(pw)
    if c["symbol"]:
        return CATEGORIES[4]
    if c["digit"] and not (c["lower"] or c["upper"]):
        return CATEGORIES[0]
    if c["digit"]:
        return CATEGORIES[3]
    if c["lower"] and not c["upper"]:
        return CATEGORIES[1]
    return CATEGORIES[2]


def capped_length(n: int) -> int:
    return min(n, LENGTH_CAP)


# ---------- Data and API helpers ----------
@st.cache_data
def load_summary() -> pd.DataFrame | None:
    if not SUMMARY_PATH.exists():
        return None
    return pd.read_csv(SUMMARY_PATH)


@st.cache_data(ttl=3600, show_spinner=False)    # This holds the cached data for an hour
def fetch_range(prefix: str) -> dict[str, int]:
    """Ask Pwned Passwords for every hash that starts with `prefix` (5 hex characters).

    Only this 5-character prefix is cached or sent. The password itself is never cached.
    """
    resp = requests.get(    # This helps send the web request 
        RANGE_URL + prefix,
        headers={"User-Agent": USER_AGENT, "Add-Padding": "true"},
        timeout=10,
    )
    resp.raise_for_status()    # This gives a reason why the request failed if it did.
    table = {}
    for line in resp.text.splitlines():
        suffix, _, count = line.partition(":")
        if suffix:
            table[suffix.strip().upper()] = int(count)
    return table


def times_seen(password: str) -> int:
    """How many times the password appears in known breaches (0 = not found)."""
    # SHA-1 is what the Pwned Passwords API requires, so we have to compare with hashes.
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = digest[:5], digest[5:]
    return fetch_range(prefix).get(suffix, 0)


# This records how many times the hash is seen
def analyze(password: str) -> dict:
    """Return ONLY derived facts. The password itself is not kept."""
    result = {
        "length": len(password),
        "category": category(password),
        "count": None,
        "error": None,
    }
    try:
        result["count"] = times_seen(password)
    except requests.RequestException:
        result["error"] = "Couldn't reach the Pwned Passwords service, so the breach check was skipped."
    return result

# ---------- About ----------
st.title("How Strong is your Weakest Link?")
st.header("About data breaches")
tab1, tab2, tab3, tab4 = st.tabs([
    "What is a breach?",
    "Why breaches matter",
    "Why your password still matters",
    "What experts recommend",
])

with tab1:
    st.markdown("""
A data breach happens when private information is accessed, copied, or exposed by someone who
isn't supposed to have it, for example when attackers exploit a weakness in a company's systems
or steal employees' logins. The exposed information can include email addresses, passwords,
names, phone numbers, home addresses, and payment or health details.

Well-run companies don't store passwords as plain text. They store a hash, a one-way scrambled
version that can't be directly turned back into the original, so a breach usually gives
attackers hashes, not passwords.

Attackers can still guess a likely password, scramble it the same way, and check for a match,
which is why weak and common passwords get recovered. This app works the same way: it hashes
your password and compares only part of that hash against a list of breached ones.
""")

with tab2:
    st.markdown("""
Not all breaches are equally serious. What matters most is what was exposed and how many people
it affects. A leaked email address is an annoyance, but some information, like a Social
Security number or a medical record, can't easily be changed and stays sensitive for life.

Health care organizations such as hospitals and insurers hold diagnoses, treatment records,
insurance IDs, and Social Security numbers, so a breach there generally does far more harm than
one at a small business that only holds names and emails. Stolen health information can be used
for identity theft and insurance fraud, and health organizations usually have stricter legal
duties to protect it. Larger organizations also tend to hold records on many more people, so one
incident can reach many more victims.

The overall scale is large: in one year (March 2016 to March 2017), Google researchers
identified 1.9 billion usernames and passwords exposed through breaches and traded on
black-market forums.
""")

with tab3:
    st.markdown("""
A breach doesn't automatically put your accounts at risk. If your password is long,
unpredictable, and unique, the stolen hash of it can't realistically be turned back into your
password. But if the company stored passwords poorly, or you used the same password elsewhere,
even a strong password won't save you.

Passwords are often called the weakest link because people create them, and people are
predictable. A study of 70 million passwords found that they offered little protection against
guessing, and that every group of users studied chose similarly weak ones. Because attackers
can test guesses against stolen hashes at their own speed, weak choices fall quickly: in this
app's own sample, 85% of the leaked passwords were 8 characters or shorter.

What turns one breach into many compromised accounts is password reuse. One study estimated that
43 to 51% of users reuse the same password across sites, and that an attacker holding a leaked
password can guess a person's other passwords far more easily, because people make small,
predictable changes to a base password. Google researchers found that 7 to 25% of exposed
passwords matched the victim's Google account, and access to an email account can unlock the
rest of a person's online identity.
""")

with tab4:
    st.markdown("""
The Federal Trade Commission recommends passwords of at least 12 characters. It advises avoiding
common phrases, song lyrics, and movie quotes, which are easy for a hacking program to guess,
and says a passphrase should be made of random words. If a site doesn't allow long passwords,
mix uppercase and lowercase letters, numbers, and symbols.

Because long, random passwords are hard to remember, the FTC suggests letting a browser or
password manager create and store them. It also recommends multi-factor authentication, so a
stolen password alone isn't enough to log in. An authenticator app or security key is stronger
than codes sent by text or email.

If a company says it lost your password in a data breach, the FTC advises changing it right
away, along with any other account that used the same or a similar password. It also stresses
protecting your email account with a strong password, since reset links are sent there.
""")

with st.expander("Sources"):
    st.markdown("""
- Bonneau, J. (2012). *The Science of Guessing: Analyzing an Anonymized Corpus of 70 Million
Passwords.* IEEE Symposium on Security and Privacy.
- Das, A., Bonneau, J., Caesar, M., Borisov, N., & Wang, X. (2014). *The Tangled Web of Password
Reuse.* NDSS Symposium.
- Federal Trade Commission. (2024). [*Creating strong passwords and other ways to protect your
accounts.*](https://consumer.ftc.gov/articles/creating-strong-passwords-and-other-ways-protect-your-accounts)
Consumer Advice.
- Thomas, K., et al. (2017). *Data breaches, phishing, or malware? Understanding the risks of
stolen credentials.* Google.
""")

# ---------- Input ----------
def run_check() -> None:    # Just changes the session state
    """Form callback: read the password, wipe it from session state, keep only derived facts."""
    typed = st.session_state.get("pw_input", "")
    example = st.session_state.get("example_choice", "(none)")
    st.session_state["pw_input"] = ""  # wipe the stored input right away
    candidate = typed or ("" if example == "(none)" else example)
    if not candidate:
        st.session_state["input_error"] = True  # keep any earlier result on screen
        return
    st.session_state["input_error"] = False
    st.session_state["result"] = analyze(candidate) 

# Sets up the widgets for password selection (typed or dropdown of examples)
st.header("Check a password")
st.info(
    "**Privacy:** your password is hashed and only the first 5 characters of the hash are sent to "
    "[Have I Been Pwned](https://haveibeenpwned.com/Passwords) (k-anonymity). This app never stores or "
    "logs what you type, and the box clears after you submit. Still, **don't enter a password you "
    "currently use**. Try one that is similar in style, or pick an example."
)
with st.form("check_form", clear_on_submit=True):
    st.text_input("Password to check", type="password", max_chars=128, key="pw_input")
    st.selectbox("Or try an example", ["(none)"] + EXAMPLES, key="example_choice")
    st.form_submit_button("Check password", on_click=run_check)

if st.session_state.get("input_error"):
    st.error("Type a password or pick an example first.")

result = st.session_state.get("result")

# ---------- Results ----------
if result:
    st.subheader("Your result")
    if result["error"]:
        st.warning(result["error"])

    count = result["count"] # This checks to see how many times that password has been seen in a data breach (API)
    if count is None:
        pass 
    elif count > 0:
        st.error(f"This password has been seen **{count:,} times** in known data breaches. Don't use it anywhere.")
    else:
        st.success(
            "This password was **not found** in known breaches. That does not mean it is strong. "
            "Long, unique passwords are what protect you."
        )

    m1, m2, m3 = st.columns(3)
    m1.metric("Seen in breaches", "Unknown" if count is None else f"{count:,} times")
    m2.metric("Length", f"{result['length']} characters")
    m3.metric("Character mix", result["category"])

# ---------- Charts ----------
st.header("Visualizing Data Leaks")
summary = load_summary()

st.subheader("How long are leaked passwords?")  # Helps users visualize how length affects password complexity, and where their password sits in this data.
if summary is None:
    st.warning("data/leaked_summary.csv not found. Make sure the data folder is in your repo.")
else:
    total = summary["passwords"].sum()  # The charts use the sample csv from the API, just trimmed (6,845)
    lengths = list(range(1, LENGTH_CAP + 1))
    by_len = summary.groupby("length")["passwords"].sum().reindex(lengths, fill_value=0) / total * 100
    labels = [str(n) if n < LENGTH_CAP else f"{LENGTH_CAP}+" for n in lengths]

    fig1 = go.Figure()
    fig1.add_bar(x=labels, y=by_len.values, name="Leaked passwords", marker_color=GREY)
    if result:
        mine = capped_length(result["length"])
        fig1.add_bar(x=[labels[mine - 1]], y=[by_len.iloc[mine - 1]], name="Your password", marker_color=PURPLE)
    fig1.update_layout(
        title="Length of leaked passwords vs. yours",
        xaxis={"title": "Password length (characters)", "type": "category"},
        yaxis_title="Share of leaked passwords (%)",
        barmode="overlay", legend_title_text="",
    )
    st.plotly_chart(fig1, width="stretch")

    st.subheader("What are leaked passwords made of?")  # Helps users visualize how complexity (adding numbers and symbols) makes it harder for someone to use your password.
    by_cat = summary.groupby("category")["passwords"].sum().reindex(CATEGORIES, fill_value=0) / total * 100
    mine_cat = CATEGORIES.index(result["category"]) if result else None
    cat_greys = ["#c3c8d1", "#aab1bd", "#8c93a0", "#6f7787", "#565e6e"]
    fig2 = go.Figure(go.Pie(
        labels=CATEGORIES,
        values=by_cat.values,
        sort=False,  # keep the categories in a fixed order
        marker={"colors": [PURPLE if i == mine_cat else cat_greys[i] for i in range(len(CATEGORIES))],
                "line": {"color": "white", "width": 2}},
        pull=[0.1 if i == mine_cat else 0 for i in range(len(CATEGORIES))],
        texttemplate="%{percent:.1%}",
        textposition="outside",  # keeps small slices readable
    ))
    fig2.update_layout(
        title="Character mix of leaked passwords" + (" (your password's group is orange)" if result else ""),
        legend_title_text="Kind of characters used",
    )
    st.plotly_chart(fig2, width="stretch")

# ---------- Insights ----------
st.header("Insights")
if summary is not None:
    short = summary.loc[summary["length"] <= 8, "passwords"].sum() / total * 100
    with_symbols = summary.loc[summary["category"] == CATEGORIES[4], "passwords"].sum() / total * 100
    st.write(
        f"In the leaked sample, **{short:.0f}%** of passwords are 8 characters or shorter and only "
        f"**{with_symbols:.1f}%** contain a symbol. Attackers know people choose short, simple passwords, "
        "so those are the first ones they try."
    )

st.divider()
st.caption(
    "Breach check: [Pwned Passwords](https://haveibeenpwned.com/Passwords) by Have I Been Pwned. "
    "Leaked-password sample: public dataset from [robinske/password-data](https://github.com/robinske/password-data) "
)
