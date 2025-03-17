import csv
import requests


def main():
    name = input("Hello, What's your name? ").strip()
    user_library = UserLibrary(name)
    user_library.load_library()

    #HOMEPAGE
    while True:
        print(f"\nHello {name}, what would you like to do today?")
        print("1. Shelf a book")
        print("2. Review my library")
        print("3. Look up a book")
        print("4. Update book progress")
        print("5. Exit")
        choice = input("Choose an option 1-5: ").strip()

        #SHELF A BOOK
        if choice == "1":

            title = get_title()
            if title is None:
                continue #(go back to Homepage)

            if user_library.does_book_exist(title):
                print(f"{title} is already in your library!")
                continue

            progress = get_progress(title)
            if progress is None:
                continue
            rating = None

            if progress == "Finished":
                rating = get_rating()
                if rating is None:
                    continue #(go back to Homepage)



            book = Book(title,rating,progress)
            user_library.add_book(book)

        #REVIEW YOUR LIBRARY
        elif choice == "2":
            print("Lets take a look! How would you like to see you library sorted by?")
            print("1. Title")
            print("2. Rating")
            print("3. Recently added")
            sort_option = input("Choose an option 1-3: ").strip()

            if sort_option == "1":
                user_library.show_library(sort_by="title")
            elif sort_option == "2":
                user_library.show_library(sort_by="rating")
            elif sort_option == "3":
                user_library.show_library(sort_by="recent")
            else:
                print("Invalid sorting option")

        #LOOK UP A BOOK
        elif choice == "3":
            title = input("What book are you looking to find? (type / to go back)")
            if title == "/":
                continue
            print("Where would you like to search?")
            print("1. In Library")
            print("2. Online")
            search_choice = input("Chose an option 1 or 2: ").strip()

            if search_choice == "1":
                if user_library.does_book_exist(title):
                    print(f"{title} is in your library")
                else:
                    print(f"{title} does not seem to be in your library...")
            elif search_choice == "2":
                API_search(title)
            else:
                print("Invalid choice.")


        #UPDATE BOOK PROGRESS
        elif choice == "4":
            title = input("What book would you like to update progresss for? (type / to go back) ")
            if title == "/":
                continue
            book = user_library.find_book_by_title(title)
            if book:
                progress = user_library.update_book_progress(book)
                if progress == "Finished":
                    rating = get_rating()
                    if rating is None:
                        continue


            else:
                print(f"{title} does not seem to be in your library...")

        #EXIT
        elif choice == "5":
            user_library.save_library()
            print("Goodbye! See you next time. ")
            break
        else:
            print("Invalid choice. Please choose an option 1-5")



def get_title():
    while True:
        title = input("What's the book title? (or '/' to go back): ").strip()
        if title == "/":
            return None
        #maybe add some restrictions to title?
        if title:
            return title
        ###invalid input??
        else:
            print("Invalid Book title, try again.")

def get_rating():
    while True:
        rating = input("How would you rate this book on a scale of 1-5? ('/' to go back): ").strip()
        if rating == "/":
            return None
        if rating.isdigit() and 1 <= int(rating) <= 5:
            return int(rating)
        else:
            print("Invalid rating, please enter a number between 1 and 5")

def get_progress(title):
    while True:
        #double check to make sure that this boko is the name of the one most recently entered.
        print (f"What's your current progress with {title}? ('/' to go back) ")
        print("1. Not started")
        print("2. In progress")
        print("3. DNF")
        print("4. Finished")

        progress = input("Enter the number of your progress: ").strip()

        if progress == "1":
            return "Not started"
        elif progress == "2":
            return "In-progress"
        elif progress == "3":
            return "DNF"
        elif progress == "4":
            return "Finished"
        elif progress == "/":
            return None
        else:
            print("Invalid Input, please enter 1,2,3,4 or /")

def API_search(title):
    OpenLibrary = "https://openlibrary.org/search.json"

    try:
        response = requests.get(OpenLibrary, params = {'title' : title})

        if response.status_code == 200:
            data = response.json()

            if data['num_found'] > 0: #if there are more than 0 results
                book = data['docs'][0] #grab the first book result

                #get title, author, description, rating
                book_title = book.get('title')
                book_author = book.get('author_name', ['No author available'])[0]
                book_key = book.get('key', '')

                details_response = requests.get(f"https://openlibrary.org{book_key}.json")
                if details_response.status_code == 200:
                    details_data = details_response.json()

                    description_field = details_data.get('description', 'No description available')
                    if isinstance(description_field, dict):
                        description = description_field.get('value','No description available')
                    else:
                        description = description_field

                    average_rating = details_data.get('average_rating', 'No rating available')

                    print(f"Title: {book_title}")
                    print(f"Author: {book_author}")
                    print(f"Rating: {average_rating}")
                    print(f"Description: {description}")
                else:
                    print("Could not retrieve book information")
            else:
                print("Could not find a book with that title.")
        else:
            print("Request to Open Library API has failed")
    except Exception as e:
        print(f"\nAn Error has occurred: {e}")




class Book:
    def __init__(self, title, rating, progress):
        self.title = title
        self.progress = progress

        if isinstance(rating, int):
            self.rating_numeric = rating
            self.rating = "⭐" * rating
        else:
            self.rating_numeric = None
            self.rating = None


    def __str__(self):
        return f"{self.title} | {self.rating if self.rating else 'Not Yet Rated'} | {self.progress}"


    def update_progress(self,progress):
        valid_progress = ["Not started", "In-progress", "DNF", "Finished"]
        if progress in valid_progress:
            self.progress = progress
        else:
            raise ValueError("Invalid progress input")


class UserLibrary:
    def __init__(self, user_name):
        self.user_name = user_name
        self.books = []

    def add_book(self,book):
        if any(b.title.lower() == book.title.lower() for b in self.books):
            print(f"{book.title} is already in your library!")
        else:
            self.books.append(book)
            print(f"{book.title} has been added to your library! :)")

    def show_library(self, sort_by="title"):
        if not self.books:
            print("hmm...Looks like your library is currently empty.")
        if sort_by == "title":
            sorted_books = sorted(self.books, key=lambda b: b.title)
        elif sort_by == "rating":
            sorted_books = sorted(self.books, key=lambda b: b.rating_numeric if b.rating_numeric else 0, reverse = True)
        elif sort_by == "recent":
            sorted_books = self.books
        else:
            print("Invalid sorting option")
            return

        print("\nYour Library:")
        for i, book in enumerate(sorted_books, 1):
            print(f"{i}. {book}")

    def find_book_by_title(self, title):
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None

    def update_book_progress(self, book):
        new_progress = get_progress(book.title)
        if new_progress:
            try:
                book.update_progress(new_progress)
                print(f"Progress for {book.title} has been updated to {book.progress}.")
            except ValueError as e:
                print(e)

    def does_book_exist(self, title):
        return any(book.title.lower() == title.lower() for book in self.books)

    def save_library(self, filename = "library.csv"):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Rating", "Progress"])
            for book in self.books:
                rating_length = len(book.rating) if book.rating else 0
                writer.writerow([book.title, rating_length, book.progress])


    def load_library(self, filename="library.csv"):
        try:
            with open(filename,"r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rating = int(row["Rating"])
                    book = Book(row["Title"], rating, row["Progress"])
                    self.books.append(book)
        except FileNotFoundError:
            print("No existing library found, lets start fresh!")

if __name__ == "__main__":
    main()