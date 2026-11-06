# Store Management — Collaboration Guide

This guide explains how to collaborate on the **Store Management** project using Git, GitHub, Excel, and Power BI.

**GitHub Repository:** https://github.com/JWulfran/Store_Management_V1

## 1. Our Responsibilities

| Project Owner | Collaborator |
|---|---|
| Django development | Excel analysis |
| Database management | Data cleaning |
| Data extraction and CSV exports | Power BI dashboards |
| ETL pipelines | Data visualization |
| GitHub management | Analytics documentation |

**Goal:** Work together to analyze retail data and build useful business dashboards.

## 2. Clone the Repository

First, install Git and configure your identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Clone the project:

```bash
git clone https://github.com/JWulfran/Store_Management_V1.git
```

Navigate into the project:

```bash
cd Store_Management_V1
```

Open the project in VS Code:

```bash
code .
```

## 3. Access Data in Excel or Power BI

The project exports four main CSV datasets:

| Dataset | Description |
|---|---|
| `categories.csv` | Product categories |
| `products.csv` | Product information and inventory |
| `purchases.csv` | Purchase transactions |
| `sales.csv` | Sales transactions |

Find these files in the project's data export directory.

### Excel

1. Open Excel.
2. Select **Data → Get Data → From Text/CSV**.
3. Select a CSV file.
4. Click **Transform Data** to clean and prepare the data.
5. Load the data and begin your analysis.

### Power BI

1. Open Power BI Desktop.
2. Select **Home → Get Data → Text/CSV**.
3. Import the CSV files.
4. Use Power Query to clean the data.
5. Create relationships between tables.
6. Build dashboards using DAX and visuals.

## 4. Git Workflow

### Step 1 — Get the latest changes

```bash
git switch main
git pull origin main
```

### Step 2 — Create your working branch

```bash
git switch -c analytics/sales-dashboard
```

### Step 3 — Work on your files

Create or update your Excel and Power BI reports.

Save them in:

```text
analysis/
├── Excel/
│   └── sales_analysis.xlsx
└── PowerBI/
    └── sales_dashboard.pbix
```

### Step 4 — Save your changes with Git

```bash
git status
git add analysis/
git commit -m "Add sales dashboard"
```

### Step 5 — Push changes to GitHub

```bash
git push -u origin analytics/sales-dashboard
```

### Step 6 — Create a Pull Request

On GitHub:

1. Open the repository.
2. Go to **Pull requests**.
3. Click **New pull request**.
4. Select your branch and compare it with `main`.
5. Submit the pull request for review.

**Important:** Do not push directly to `main`.

## 5. Update Your Data

Whenever new CSV datasets are available on GitHub:

```bash
git switch main
git pull origin main
```

Then:

- **Excel:** Data → Refresh All
- **Power BI:** Home → Refresh

If the CSV files have moved, update their source paths in Power Query.

If you are working on an existing branch, commit your changes first, then merge the updated `main` into your branch.

## 6. Useful Git Commands

| Command | Purpose |
|---|---|
| `git clone <URL>` | Download the repository |
| `git status` | Check modified files |
| `git pull origin main` | Get latest updates |
| `git switch -c <branch>` | Create a branch |
| `git add analytics/` | Stage analytics files |
| `git commit -m "message"` | Save changes |
| `git push -u origin <branch>` | Upload your branch |
| `git branch` | List local branches |


## 7. Collaboration Rules

1. Always work on a separate Git branch.
2. Keep Excel and Power BI files inside `analytics/`.
3. Do not modify the original CSV datasets.
4. Use clear commit messages.
5. Create a pull request for each completed task.
6. Never upload passwords, `.env` files, or sensitive data.
7. Coordinate changes to the same Power BI file to avoid conflicts.

---

**Let's collaborate, learn, and build a great Data Analytics project together! 🚀**