# Name:Leila Sarkamari
# Lab 3-CIS 41B 
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
conn = sqlite3.connect('TravelDestination.db')
cur = conn.cursor() 
class MainWindow(tk.Tk):
    '''
    The GUI main window has a title , a “Search by” string, and 3 buttons that the search will base on the selection buttons
    and will display GUI dialog window
    '''
    def __init__(self):
        super().__init__()
        self.title("Best places to travel in 2024")
        self.configure(bg="#e0f7fa")
        self.geometry("300x100")
        
        self.title_label = tk.Label(self, text="Best places to travel in 2024", font=("Helvetica", 18, "bold"),bg="#e0f7fa")
        self.title_label.grid(row=1,columnspan=4)

        self.search_label = tk.Label(self, text="Search by:", font=("Helvetica", 14),fg="blue", bg="#e0f7fa")
        self.search_label.grid(row=2,column=0,pady=3)

        self.name_button = tk.Button(self, text="Name",font=("Helvetica", 14,"bold"),fg="#336699",command=self.search_by_name)
        self.name_button.grid(row=2,column=1,pady=3)

        self.month_button = tk.Button(self, text="Month",font=("Helvetica", 14,"bold"),fg="#336699" , command=self.search_by_month)
        self.month_button.grid(row=2,column=2,pady=3)

        self.rank_button = tk.Button(self, text="Rank",font=("Helvetica", 14,"bold"),fg="#336699", command=self.search_by_rank)
        self.rank_button.grid(row=2,column=3,pady=3)
        self.protocol("WM_DELETE_WINDOW", self.destroy)


    def search_by_name(self):
        dialog = DialogWindow(self, "name")
        self.wait_window(dialog)
        if dialog.result:
            self.show_results("name", dialog.result)

    def search_by_month(self):
        dialog = DialogWindow(self, "month")
        self.wait_window(dialog)
        if dialog.result:
            self.show_results("month", dialog.result)

    def search_by_rank(self):
        dialog = DialogWindow(self, "rank")
        self.wait_window(dialog)
        if dialog.result:
            self.show_results("rank", dialog.result)

    def show_results(self, criterion, choice):
        results_window = ResultWindow(self, criterion, choice)
        self.wait_window(results_window)

class DialogWindow(tk.Toplevel):
    '''
    the DialogWindow will display an appropriate instruction to tell the user to click on a radio button
    '''
    def __init__(self, parent, criterion):
        super().__init__(parent)
        self.parent = parent
        self.criterion = criterion
        self.result = None
        self.transient(parent)
        self.grab_set()
        
        if criterion == "name":
            self.title("Search by Name")
            instruction = "Click on a letter to select"
            options = self.get_names()
        elif criterion == "month":
            self.title("Search by Month")
            instruction = "Click on a month to select"
            options = self.get_months()
        else:  # criterion == "rank"
            self.title("Search by Rank")
            instruction = "Click on a rank to select"
            options = self.get_ranks()
        
        tk.Label(self, text=instruction, anchor='w').pack(pady=10)
        self.var = tk.StringVar(value=options[0])
        

        for option in options:
            tk.Radiobutton(self, text=option, variable=self.var, value=option, anchor='w').pack(anchor='w')

        tk.Button(self, text="OK", command=self.on_ok).pack(pady=10)

    def get_names(self):
        cur.execute("SELECT DISTINCT SUBSTR(name, 1, 1) AS initial FROM CityInfo ORDER BY initial")
        initials = [row[0] for row in cur.fetchall()]

        #print(f"Initials: {initials}")  # Debug 
        return initials

    def get_months(self):
        cur.execute("SELECT month FROM Months ORDER BY id")
        months = [row[0] for row in cur.fetchall()]
        #print(f"Months: {months}")  # Debug 
        return months

    def get_ranks(self):
        cur.execute("SELECT MAX(rank) FROM CityInfo")
        max_rank =cur.fetchone()[0]
        ranks = [str(rank) for rank in range(1, max_rank + 1)]
        #print(f"Ranks: {ranks}")  # Debug 
        return ranks
   
    def on_ok(self):
        self.result = self.var.get()
        self.grab_release()
        self.destroy()

class ResultWindow(tk.Toplevel):
    '''
    The result window has:
    A description appropriate for the search criteria. See samples below.
    A listbox that can display 10 lines of text.
    A scrollbar, since there could be more than 10 lines of data.

    '''
    def __init__(self, parent, criterion, choice):
        super().__init__(parent)
        self.parent = parent
        self.criterion = criterion
        self.choice = choice
        self.transient(parent)
        self.grab_set()

        if criterion == "name":
            self.title(f"Destinations starting with {choice}")
            description = f"Destinations starting with {choice}"
            results = self.get_results_by_name(choice)
        elif criterion == "month":
            self.title(f"Top destinations for {choice}")
            description = f"Top destinations for {choice} in ranking order"
            results = self.get_results_by_month(choice)
        else:  # criterion == "rank"
            self.title(f"Destinations with rank {choice}")
            description = f"Destinations with rank {choice} for the listed months"
            results = self.get_results_by_rank(choice)

        tk.Label(self, text=description, anchor='w').pack(pady=10)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        for item in results:
            self.listbox.insert(tk.END, item)

        self.listbox.bind("<<ListboxSelect>>", self.on_select)

    def get_results_by_name(self, initial):

        cur.execute("SELECT DISTINCT name FROM CityInfo WHERE name LIKE ? ORDER BY name", (initial + '%',))
        results = [row[0] for row in cur.fetchall()]
        #print(f"Results by name ({initial}): {results}")  # Debug 
        return results

    def get_results_by_month(self, month):
        cur.execute("SELECT CityInfo.name, CityInfo.rank FROM CityInfo JOIN Months ON CityInfo.month_id = Months.id WHERE Months.month = ? ORDER BY CityInfo.rank", (month,))
        results = [f"{row[1]}. {row[0]}" for row in cur.fetchall()]
        #print(f"Results by month ({month}): {results}")  # Debug 
        return results

    def get_results_by_rank(self, rank):
        cur.execute("SELECT CityInfo.name, Months.month FROM CityInfo JOIN Months ON CityInfo.month_id = Months.id WHERE CityInfo.rank = ? ORDER BY Months.id", (rank,))
        results = [f"{row[0]} ({row[1]})" for row in cur.fetchall()]
        #print(f"Results by rank ({rank}): {results}")  # Debug 
        return results

    def on_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            value = event.widget.get(index)
            #print("value=",value)
            if self.criterion == "name":
                destination = value                #exp:value=Adelaide Australia
            elif self.criterion == "month":
                destination = value.split('. ')[1] #exp:value=1. Melbourne
            else:  # criterion == "rank"
                destination = value.split(' (')[0] #exp:value=Cape Town (January)

            DisplayWindow(self, destination)

class DisplayWindow(tk.Toplevel):
    '''
    The display window has:
    The destination name.
    The description paragraph.

    '''
    def __init__(self, parent, destination):
        super().__init__(parent)
        self.parent = parent
        self.transient(parent)
        self.grab_set()
        cur.execute("SELECT description, destination_url FROM CityInfo WHERE name = ?", (destination,))
        row = cur.fetchone()

        description, url = row if row else ("Description not found", None)

        self.title(destination)
        self.configure(bg="#f0f4c3")
        tk.Label(self, text=destination, font=("Helvetica", 16, "bold"), bg="#f0f4c3").pack(pady=10)
        tk.Label(self, text=description, wraplength=300, bg="#f0f4c3").pack(pady=10)

        if url and url != "None":
            tk.Button(self, text=f"See {destination} details", command=lambda: webbrowser.open(url)).pack(pady=10)

if __name__ == "__main__":
    main_window = MainWindow()
    main_window.mainloop()
    conn.close()

