class TableItems(object):

    def __init__(self, table, hidden_column, numeric_column):
        self.table = table
        self.hidden_column = hidden_column
        self.numeric_column = numeric_column

    def build(df):

        # Clear existing contents
        self.table.clear() # This is important!
        while (self.table.rowCount() > 0):
            self.table.removeRow(0)

        # Create new table
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(df.columns.tolist())
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().hide()
        # Hidden columns
        for i in np.arange(len(hidden_column)):
            if self.hidden_column[i]:
                self.table.setColumnHidden(i,True)

        # Add new contents
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.buildOne(i, j)

        # Tighten up the table
        self.table.resizeRowsToContents()

    def buildOne(self, df, i, j):
        if self.numeric_column[j]:
            # Guarantee that all elements are converted to strings for display but apply proper sorting
            self.table.setItem(i, j, MyNumericTableWidgetItem(str(df.iat[i,j])))

        elif df.columns[j] == 'Waveform':
            # NOTE:  What to put in the Waveform column depends on what is in the WaveformImagePath column.
            # NOTE:  It could be plain text or an imageWidget.
            if df.WaveformImagePath.iloc[i] == '':
                self.table.setItem(i, j, QtGui.QTableWidgetItem(''))
            elif df.WaveformImagePath.iloc[i] == 'NO DATA AVAILABLE':
                self.table.setItem(i, j, QtGui.QTableWidgetItem('NO DATA AVAILABLE'))
            else:
                imagePath = df.WaveformImagePath.iloc[i]
                imageItem = MyTableWidgetImageItem(imagePath)
                self.table.setItem(i, j, imageItem)

        elif df.columns[j] == 'Keep':
            checkBoxItem = QtGui.QTableWidgetItem()
            checkBoxItem.setFlags(QtCore.Qt.ItemIsEnabled)
            if df.Keep.iloc[i]:
                checkBoxItem.setCheckState(QtCore.Qt.Checked)
            else:
                checkBoxItem.setCheckState(QtCore.Qt.Unchecked)
            self.table.setItem(i, j, checkBoxItem)

        else:
            # Anything else is converted to normal text
            self.table.setItem(i, j, QtGui.QTableWidgetItem(str(df.iat[i,j])))
