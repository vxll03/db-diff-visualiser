class SchemaDiff:
    def __init__(self, old_schema, new_schema):
        self.old = old_schema
        self.new = new_schema
        self.report = {"added_tables": [], "removed_tables": [], "changed_tables": {}}

    def compare(self):
        old_tables = {t["name"]: t for t in self.old["tables"]}
        new_tables = {t["name"]: t for t in self.new["tables"]}

        all_table_names = set(old_tables.keys()) | set(new_tables.keys())

        for name in all_table_names:
            if name not in old_tables:
                self.report["added_tables"].append(name)
            elif name not in new_tables:
                self.report["removed_tables"].append(name)
            else:
                table_diff = self._compare_tables(old_tables[name], new_tables[name])
                if table_diff:
                    self.report["changed_tables"][name] = table_diff

        return self.report

    def _compare_tables(self, old_t, new_t):
        diff = {"added_columns": [], "removed_columns": [], "changed_columns": {}}

        old_cols = {c["name"]: c for c in old_t["columns"]}
        new_cols = {c["name"]: c for c in new_t["columns"]}

        all_col_names = set(old_cols.keys()) | set(new_cols.keys())

        for cname in all_col_names:
            if cname not in old_cols:
                diff["added_columns"].append(new_cols[cname])
            elif cname not in new_cols:
                diff["removed_columns"].append(cname)
            else:
                col_changes = self._compare_columns(old_cols[cname], new_cols[cname])
                if col_changes:
                    diff["changed_columns"][cname] = col_changes

        return {k: v for k, v in diff.items() if v}

    def _compare_columns(self, old_c, new_c):
        changes = {}
        for attr in ["type", "nullable", "default"]:
            if old_c[attr] != new_c[attr]:
                changes[attr] = {"old": old_c[attr], "new": new_c[attr]}
        return changes
