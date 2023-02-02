from .dlg_scroll_base import DlgScrollBase


class YesNo(DlgScrollBase):
    def __init__(self, question: str, empty_ans: bool = False) -> None:
        DlgScrollBase.__init__(self, question, empty_ans=empty_ans)
        self.sz_question = question
        self.sz_options = ["Sí", "No"]
        self.n_options = 2
        self.curr_index = 1
        self.min_index = 0

    def get_ans(self) -> bool:
        ans = DlgScrollBase.get_ans(self)

        return ans == "Sí"
