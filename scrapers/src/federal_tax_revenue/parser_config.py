"""Configuration for tax revenue file parser.  Allows the specification of custom file targets and mappings.
File patterns do not allow dynamic components except for for {date}, which will be replaced with the date from the
source file.  Attribute patterns are regex patterns."""


from collections import OrderedDict


config = {
    # Collection of files to which the parsed data is written.
    "file_targets": {
        1: {
            "file_pattern": "parsed_{date}_operating_cash_balance.csv",
            "attribute_pattern": "Operating Cash Balance::.*",
        },
        2: {
            "file_pattern": "parsed_{date}_deposits_of_operating_cash.csv",
            "attribute_pattern": "Deposits and Withdrawals of Operating Cash::Deposits::.*",
        },
        3: {
            "file_pattern": "parsed_{date}_withdrawals_of_operating_cash.csv",
            "attribute_pattern": "Deposits and Withdrawals of Operating Cash::Withdrawals::.*",
        },
        4: {
            "file_pattern": "parsed_{date}_public_debt_issues.csv",
            "attribute_pattern": "Public Debt Transactions::Issues::.*",
        },
        5: {
            "file_pattern": "parsed_{date}_public_debt_redemptions.csv",
            "attribute_pattern": "Public Debt Transactions::Redemptions::.*",
        },
        6: {
            "file_pattern": "parsed_{date}_adj_of_public_debt_trans_to_cash_basis.csv",
            "attribute_pattern": "Adjustment of Public Debt Transactions to Cash Basis::.*",
        },
        7: {
            "file_pattern": "parsed_{date}_debt_subject_to_limit.csv",
            "attribute_pattern": "Debt Subject to Limit::.*",
        },
        8: {
            "file_pattern": "parsed_{date}_federal_tax_deposits.csv",
            "attribute_pattern": "Federal Tax Deposits::.*",
        },
        9: {
            "file_pattern": "parsed_{date}_short_term_cash_investments.csv",
            "attribute_pattern": "Short-Term Cash Investments::.*",
        },
        10: {
            "file_pattern": "parsed_{date}_income_tax_refunds_issued.csv",
            "attribute_pattern": "Income Tax Refunds Issued::.*",
        },
        # insert custom file targets below

    },

    # Define custom mapping overrides here. An example entry:
    # {
    #   "file_pattern": "Public Debt Transactions::Redemptions::Marketable::*",
    #   "file_id": 11,
    # }
    # This will divert any entries matching the specified tag to the file corresponding to ID 11.
    # These rows will no longer be written to their default location in file 5.
    # Order matters; in the case of multiple overrides that apply to the same row, the latest entry will be applied.
    "mapping_overrides": OrderedDict([
        # insert custom mappings below

    ])

}
