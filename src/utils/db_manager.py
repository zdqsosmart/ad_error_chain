import os
import logging
from typing import Optional, List, Dict

import pandas as pd
from psycopg2 import pool
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

from src.utils.mylog import getMyLog

load_dotenv("../../.env")
db_logger = getMyLog()


class PostgreManager:
    # 单例模式，全局唯一连接池
    _instance: Optional["SyncPGDBManager"] = None
    _connection_pool: Optional[pool.SimpleConnectionPool] = None

    def __new__(cls):
        # 单例：确保全局仅创建一个DBManager实例
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def init_pool(self):
        """初始化同步连接池（全局仅执行一次）"""
        if self._connection_pool is None:
            try:
                self._connection_pool = pool.SimpleConnectionPool(
                    minconn=int(os.getenv("PG_MIN_CONN")),
                    maxconn=int(os.getenv("PG_MAX_CONN")),
                    host=os.getenv("PG_HOST"),
                    port=os.getenv("PG_PORT"),
                    user=os.getenv("PG_USER"),
                    password=os.getenv("PG_PASSWORD"),
                    dbname=os.getenv("PG_DATABASE"),
                    options="-c client_encoding=utf8"  # 解决中文乱码
                )
                db_logger.info("PostgreSQL 同步连接池初始化成功")
            except Exception as e:
                db_logger.error(f"连接池初始化失败: {str(e)}")
                raise

    def close_pool(self):
        """关闭连接池，释放所有数据库资源"""
        if self._connection_pool:
            self._connection_pool.closeall()
            db_logger.info("数据库连接池已全部关闭")

    # 上下文管理器支持：with 语句自动初始化/关闭连接池
    def __enter__(self):
        self.init_pool()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_pool()

    # -------------------------- 私有方法：获取/释放连接 --------------------------
    def _get_conn(self):
        """从连接池获取连接"""
        return self._connection_pool.getconn()

    def _release_conn(self, conn):
        """释放连接回连接池"""
        if conn:
            self._connection_pool.putconn(conn)

    # -------------------------- 通用数据库操作 --------------------------
    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict]:
        """查询单条数据，返回字典格式"""
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                return cur.fetchone()
        except Exception as e:
            db_logger.error(f"查询单条数据失败: {e}")
            conn.rollback()
            raise
        finally:
            self._release_conn(conn)

    def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict]:
        """查询多条数据，返回字典列表"""
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception as e:
            db_logger.error(f"查询批量数据失败: {e}")
            conn.rollback()
            raise
        finally:
            self._release_conn(conn)

    def fetch_all_then_return_dataframe(self, sql: str) -> pd.DataFrame:
        """执行SQL并返回Pandas DataFrame"""
        try:
            conn = self._get_conn()
            df = pd.read_sql(sql, con=conn)
            return df
        except Exception as e:
            db_logger.error(f"fetch_all_then_return_dataframe:{e}")

    def execute(self, sql: str, params: tuple = ()) -> str:
        """执行增删改操作，返回执行结果"""
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                conn.commit()
                return cur.statusmessage
        except Exception as e:
            conn.rollback()
            db_logger.error(f"执行SQL失败: {e}")
            raise
        finally:
            self._release_conn(conn)

    def execute_transaction(self, sql_list: List[tuple]):
        """批量事务操作：全部成功提交，任意失败回滚"""
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                for sql, params in sql_list:
                    cur.execute(sql, params)
                conn.commit()
                db_logger.info("批量事务执行完成")
        except Exception as e:
            conn.rollback()
            db_logger.error(f"事务执行失败，已回滚: {e}")
            raise
        finally:
            self._release_conn(conn)


class Redis:
    pass


if __name__ == "__main__":
    # 上下文管理器自动管理资源（推荐）
    with PostgreManager() as db:
        res = db.fetch_all_then_return_dataframe(
            "select distinct entity,note from business.amazon_advertising_auto_table")
        for item in res.itertuples():
            print(item)
