class SQL_String():

    @staticmethod
    def create_table_orders():
        '''
            Returns SQL script to create table Orders with following columns:
                id              INTEGER     PRIMARY KEY AUTOINCREMENT,
                created_date    TEXT        NOT NULL, 
                merchant_id     INTEGER     NOT NULL
        '''
        # It was decided to use TEXT datatype for storing dates.
        return f'''
            CREATE TABLE IF NOT EXISTS Orders (
                id              INTEGER     PRIMARY KEY AUTOINCREMENT,
                created_date    TEXT        NOT NULL, 
                merchant_id     INTEGER     NOT NULL
            );
        '''
    
    @staticmethod
    def create_table_transactions():
        '''
            Returns SQL script to create table Transactions with following columns:
                id                  INTEGER     PRIMARY KEY AUTOINCREMENT, 
                created_date        TEXT        NOT NULL, 
                transaction_type    TEXT        NOT NULL, 
                order_id            INTEGER     NOT NULL, 
                transaction_status  TEXT        NOT NULL
            And 2 constraints: 
                CHECK (transaction_type IN ('auth', 'settle', 'void'))
                CHECK (transaction_status IN ('success', 'fail'))
                FOREIGN KEY(order_id) REFERENCES Orders(id)
        '''
        return f'''
            CREATE TABLE IF NOT EXISTS Transactions (
                id                  INTEGER     PRIMARY KEY AUTOINCREMENT, 
                created_date        TEXT        NOT NULL, 
                transaction_type    TEXT        NOT NULL    CHECK (transaction_type IN ('auth', 'settle', 'void')), 
                order_id            INTEGER     NOT NULL, 
                transaction_status  TEXT        NOT NULL    CHECK (transaction_status IN ('success', 'fail')),
                FOREIGN KEY(order_id) REFERENCES Orders(id)
            )
        '''
    
    @staticmethod
    def insert_into_orders(order_info):
        '''
            Returns SQL script for insertion data into Orders table.
            Required argument `order_info` should be one order.
        '''
        return f'''
            INSERT INTO Orders 
            VALUES 
            ({order_info[0]}, '{order_info[1]}', {order_info[2]})
        ''' 
    
    @staticmethod
    def insert_into_transactions(tr_info):
        '''
            Returns SQL script for insertion data into Transactions table.
        '''
        return f'''
            INSERT INTO Transactions (created_date, transaction_type, order_id, transaction_status) 
            VALUES 
            ('{tr_info[0]}', '{tr_info[1]}', {tr_info[2]}, '{tr_info[3]}')
        '''
    
    @staticmethod
    def get_not_finished_transactions_query():
        '''
            Returns query to check for not finished payments.
        '''
        return f'''
            with auth_transactions as (
                select * 
                from Transactions
                where transaction_type = "auth"
                    and transaction_status = "success"
            ),
            second_transactions as (
                select *
                from Transactions
                where (transaction_type = "settle"
                    or transaction_type = "void")
                    and transaction_status = "success"
            )
            select a.*,
                o.merchant_id
            from auth_transactions as a
            left join second_transactions as s
            on (a.order_id = s.order_id)
            left join Orders as o
            on (a.order_id = o.id)
            where a.created_date < datetime(strftime("%Y-%m-%d %H:%M:%f", "now"), "-7 day")
                and s.order_id is null
        '''