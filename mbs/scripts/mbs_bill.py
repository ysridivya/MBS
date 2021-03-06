import os
from datetime import datetime
from mbs.commons import load_database_config, get_config_file_path
from mbs.mbs_database_access import execute_query, set_config, insert_details
from mbs.mbs_exceptions import InsertionFailed, BillGenerationFailed


def get_bill_for_the_month(config_path):
    db_config = load_database_config(config_path)
    set_config(db_config)
    curr_month = datetime.today().month
    curr_year = datetime.today().year
    sql_query = " select T_id,cost,billed_key from monthly_bill where MONTH(billed_time) = %s and YEAR(billed_time)= %s"
    parms = (curr_month, curr_year,)
    db_result = execute_query(sql_query, parms, 1)
    return db_result


def update_db_with_bill(db_result):
    curr_time = datetime.now()
    billed_key = curr_time.strftime('%Y%m')
    sql_drop_query = """Delete from monthly_bill"""
    execute_query(sql_drop_query)

    try:
        sql_insert_query = """ INSERT INTO bill_history(T_id, billed_time, cost,billed_key) VALUES (%s,%s,%s,%s) """
        sql_insert_query2 = """ INSERT INTO monthly_bill(T_id, billed_time, cost,billed_key) VALUES (%s,%s,%s,%s) """

        for result in db_result:
            print(result)
            parms = (result['T_id'], curr_time, result['price'], billed_key)
            result = insert_details(sql_insert_query, parms)
            result = insert_details(sql_insert_query2, parms)

    except InsertionFailed as e:
        raise BillGenerationFailed(str(e))


def generate_bill(month):
    config_path  = get_config_file_path(str(os.path.realpath(__file__)))
    db_config = load_database_config(config_path)
    set_config(db_config)
    sql_query = " select T_id,sum(cost) as price from purchase_order where MONTH(purchase_time) = %s group by T_id"
    parms = (month,)
    db_result = execute_query(sql_query, parms, 1)

    try:
        update_db_with_bill(db_result)

    except Exception as e:
        print(e)
