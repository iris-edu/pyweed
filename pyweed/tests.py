from time import sleep

def gui_test(pyweed):
    pyweed.fetch_events()
    pyweed.fetch_stations()
    sleep(2)
    for i in range(5):
        pyweed.mainWindow.eventsTable.selectRow(i)
    for i in range(5):
        pyweed.mainWindow.stationsTable.selectRow(i)
    pyweed.openWaveformsDialog()
