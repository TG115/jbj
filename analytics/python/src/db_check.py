import os

import pymysql


def main() -> None:
    connection = pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_DATABASE"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    VERSION() AS mysql_version,
                    DATABASE() AS database_name
                """
            )

            database_info = cursor.fetchone()

            cursor.execute(
                """
                SELECT COUNT(*) AS taxonomy_count
                FROM occupation_taxonomy
                """
            )

            taxonomy = cursor.fetchone()

            cursor.execute(
                """
                SELECT COUNT(*) AS node_count
                FROM occupation_taxonomy_node
                """
            )

            nodes = cursor.fetchone()

        print("JBJ Python DB connection: OK")
        print(f"MySQL: {database_info['mysql_version']}")
        print(f"Database: {database_info['database_name']}")
        print(f"Taxonomies: {taxonomy['taxonomy_count']}")
        print(f"Taxonomy nodes: {nodes['node_count']}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()