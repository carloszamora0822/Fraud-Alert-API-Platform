"""
ADX Client — wraps the Azure Data Explorer Python SDK.

This module handles connecting to our ADX cluster and running KQL queries.
The rest of the app never touches the SDK directly — it goes through this client.

Authentication: For the free cluster, we use Azure's "device code" flow —
when you first connect, it prints a URL + code to your terminal. You open the
URL in a browser, paste the code, and log in with your Microsoft account.
After that, the token is cached so you don't have to do it every time.
"""

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.response import KustoResponseDataSet

from app.core.config import settings


class ADXClient:
    """
    Thin wrapper around the Kusto SDK.

    Why a wrapper? Same reason we have a service layer for PostgreSQL —
    it keeps SDK-specific code in one place. If Microsoft changes their SDK,
    we only update this file.
    """

    def __init__(self) -> None:
        # KustoConnectionStringBuilder is like SQLAlchemy's create_engine() —
        # it configures HOW to connect (cluster URL + auth method).
        # with_interactive_login() uses your browser to authenticate.
        kcsb = KustoConnectionStringBuilder.with_interactive_login(
            settings.ADX_CLUSTER_URI
        )
        self.client = KustoClient(kcsb)
        self.database = settings.ADX_DATABASE

    def execute_query(self, query: str) -> KustoResponseDataSet:
        """
        Run a KQL query against our ADX database and return the raw response.

        This is the single entry point for ALL KQL queries in the app.
        Analytics endpoints (Sprint 3.4) will call this with different queries.
        """
        return self.client.execute(self.database, query)

    def query_to_dicts(self, query: str) -> list[dict]:
        """
        Run a KQL query and return results as a list of dictionaries.

        Convenience method — converts ADX's tabular response into
        Python dicts that FastAPI can serialize to JSON directly.
        """
        response = self.execute_query(query)

        # ADX responses contain one or more "tables" of results.
        # primary_results[0] is the main result table.
        primary_table = response.primary_results[0]

        # Get column names from the table schema
        columns = [col.column_name for col in primary_table.columns]

        # Convert each row into a dict: {"column_name": value, ...}
        return [dict(zip(columns, row)) for row in primary_table.rows]

    def test_connection(self) -> bool:
        """
        Quick health check — runs a trivial KQL query to verify we can
        reach the cluster and authenticate.

        Returns True if connected, raises an exception if not.
        """
        result = self.query_to_dicts(".show database schema")
        return len(result) > 0


# Singleton instance — import this where needed.
# We create one client and reuse it, just like our `settings` singleton.
adx_client = ADXClient()
