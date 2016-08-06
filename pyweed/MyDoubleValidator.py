# Improvement to QDoubleValidator that pays attention to ranges
#
# from https://gist.github.com/jirivrany/4473639

from PyQt4.QtGui import QDoubleValidator, QValidator

from sys import float_info

class MyDoubleValidator(QDoubleValidator):
    '''
    Fix for strange behavior of default QDoubleValidator
    '''

    def __init__(self, bottom = float_info.min, \
                 top = float_info.max, \
                 decimals = float_info.dig, parent = None):
        
        super(MyDoubleValidator, self).__init__(bottom, top, decimals, parent)

    def validate(self, input_value, pos):
        
        state, pos = QDoubleValidator.validate(self, input_value, pos)
        
        if input_value.isEmpty() or input_value == '.':
            return QValidator.Intermediate, pos
        
        if state != QValidator.Acceptable:
            return QValidator.Invalid, pos
        
        return QValidator.Acceptable, pos
    
    
