/* ==========================================
   EXPENSE DATA
========================================== */

window.EXPENSE_DATA = [

{
    id: 1,
    date: "2026-07-01",
    month: "2026-07",
    weekday: "Wednesday",
    merchant: "Salary",
    category: "Income",
    amount: 75000,
    note: "Monthly Salary",
    type: "income"
},

{
    id: 2,
    date: "2026-07-12",
    month: "2026-07",
    weekday: "Sunday",
    merchant: "Swiggy",
    category: "Food",
    amount: 420,
    note: "Lunch",
    type: "expense"
},

{
    id: 3,
    date: "2026-07-15",
    month: "2026-07",
    weekday: "Wednesday",
    merchant: "Uber",
    category: "Travel",
    amount: 650,
    note: "Office Ride",
    type: "expense"
},

{
    id: 4,
    date: "2026-07-17",
    month: "2026-07",
    weekday: "Friday",
    merchant: "Unknown",
    category: "Other",
    amount: 130,
    note: "",
    type: "expense"
}

];


/* ==========================================
   DASHBOARD CONFIG
========================================== */

window.EXPENSE_CONFIG = {

    currency: "₹",
    budget: 100000

};


/* ==========================================
   CALCULATE DASHBOARD STATS
========================================== */

(function () {

    const transactions = window.EXPENSE_DATA;
    const budget = window.EXPENSE_CONFIG.budget;

    let income = 0;
    let expense = 0;

    const categoryTotals = {};
    const merchantTotals = {};
    const monthlyTotals = {};

    transactions.forEach(txn => {

        const amount = Number(txn.amount) || 0;

        if (txn.type === "income") {

            income += amount;

        } else {

            expense += amount;

            categoryTotals[txn.category] =
                (categoryTotals[txn.category] || 0) + amount;

            merchantTotals[txn.merchant] =
                (merchantTotals[txn.merchant] || 0) + amount;
        }

        if (txn.month) {

            monthlyTotals[txn.month] =
                (monthlyTotals[txn.month] || 0) + amount;

        }

    });

    const savings = income - expense;

    const budgetLeft = budget - expense;

    const today = new Date().getDate();

    const dailyAverage =
        expense / Math.max(today, 1);

    const projected =
        dailyAverage * 30;

    let topCategory = "";
    let topCategoryValue = 0;

    Object.entries(categoryTotals).forEach(([name, value]) => {

        if (value > topCategoryValue) {

            topCategoryValue = value;
            topCategory = name;

        }

    });

    let topMerchant = "";
    let topMerchantValue = 0;

    Object.entries(merchantTotals).forEach(([name, value]) => {

        if (value > topMerchantValue) {

            topMerchantValue = value;
            topMerchant = name;

        }

    });

    window.EXPENSE_STATS = {

        income,

        expense,

        savings,

        budget,

        budgetLeft,

        dailyAverage,

        projected,

        categoryTotals,

        merchantTotals,

        monthlyTotals,

        topCategory,

        topMerchant

    };

})();
