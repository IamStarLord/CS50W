import csv


f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, year in reader:
    year = int(year)
    printf(year)