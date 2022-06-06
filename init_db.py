import psycopg2


def main():
    connection = psycopg2.connect(dbname="termproject", user="postgres", password="1234")
    cur = connection.cursor()  # create cursor
    query_line = []
    for line in open("term.sql"):
        query_line.append(line)
    cur.execute("".join(query_line))
    connection.commit()
    connection.close
    print("init_db complete!")


if __name__ == "__main__":
    main()
