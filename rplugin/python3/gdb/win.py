class Win:
    def __init__(self, vim, win, cursor, client, breakpoint, keymaps):
        self.vim = vim
        # window number that will be displaying the current file
        self.jumpWin = win
        self.cursor = cursor
        self.client = client
        self.breakpoint = breakpoint
        self.keymaps = keymaps

    def jump(self, file, line):
        # Make sure all the operations happen in the correct window
        # TODO: Use api instead of Vim commands.
        window = self.vim.current.window
        mode = self.vim.api.get_mode()
        if self.jumpWin != window:
            # We're going to jump to another window and return.
            # There is no need to change keymaps forth and back.
            self.keymaps.setDispatchActive(False)
            self.vim.command("%dwincmd w" % self.jumpWin.number)

        # Check whether the file is already loaded or load it
        targetBuf = self.vim.call("bufnr", file, 1)

        # The terminal buffer may contain the name of the source file (in pdb, for
        # instance)
        if targetBuf == self.client.getBuf().handle:
            self.vim.command("noswapfile view " + file)
            targetBuf = self.vim.call("bufnr", file)

        # Switch to the new buffer if necessary
        if self.vim.call("bufnr", '%') != targetBuf:
            self.vim.command('noswapfile buffer %d' % targetBuf)

        # Goto the proper line and set the cursor on it
        self.jumpWin.cursor = (line, 0)
        self.cursor.set(targetBuf, line)
        self.cursor.show()

        # Return to the original window for the user
        if self.jumpWin != window:
            self.vim.command("%dwincmd w" % window.number)
            self.keymaps.setDispatchActive(True)
        # Restore the original mode.
        if mode['mode'] in 'ti':
            self.vim.feedkeys('a')


    def queryBreakpoints(self):
        # Get the source code buffer number
        bufNum = self.jumpWin.buffer.handle

        # Get the source code file name
        fname = self.vim.call("expand", '#%d:p' % bufNum)

        # If no file name or a weird name with spaces, ignore it (to avoid
        # misinterpretation)
        if fname and fname.find(' ') == -1:
            # Query the breakpoints for the shown file
            self.breakpoint.query(bufNum, fname)
            # If there was a cursor, make sure it stays above the breakpoints.
            self.cursor.reshow()

        # Execute the rest of custom commands
        self.vim.command("doautocmd User NvimGdbQuery")
