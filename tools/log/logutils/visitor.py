class LogEventVisitor:
    def visit_unknown(self, event):
        self.default(event)

    def visit_log_start(self, event):
        self.default(event)

    def visit_log_stop(self, event):
        self.default(event)

    def visit_sweep_start(self, event):
        self.default(event)

    def visit_sweep_done(self, event):
        self.default(event)

    def visit_allocate(self, event):
        self.default(event)

    def visit_new_arena(self, event):
        self.default(event)

    def visit_mark_start(self, event):
        self.default(event)

    def visit_mark_done(self, event):
        self.default(event)

    def visit_freelist_dump(self, event):
        self.default(event)

    def visit_allocator_switch(self, event):
        self.default(event)

    def default(self, event):
        pass
