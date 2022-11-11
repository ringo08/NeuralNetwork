
messages = {
  'menu': {
    'network': {
      'en': 'create network',
      'ja': 'ネットワーク作成'
    },
    'onehot': {
      'en': 'onehot',
      'ja': 'onehot化'
    },
    'createData': {
      'en': 'create data',
      'ja': 'データ作成'
    },
    'train': {
      'en': 'train',
      'ja': '学習'
    },
    'test': {
      'en': 'test',
      'ja': 'テスト'
    },
    'property': {
      'en': 'property',
      'ja': 'プロパティ'
    },
    'save': {
      'en': 'save',
      'ja': '保存する'
    },
    'quit': {
      'en': 'quit',
      'ja': '閉じる'
    }
  },
  'buttons': {

  },
  'dialog': {
    'title': {
      'network': {
        'en': 'create network',
        'ja': 'ネットワーク作成'
      }
    },
    'button': {
      'submit': {
        'en': 'save',
        'ja': '保存'
      },
      'create': {
        'en': 'create',
        'ja': '作成'
      },
      'cancel': {
        'en': 'cancel',
        'ja': 'キャンセル'
      }
    }
  }
}

class Messages:
  def __init__(self, config):
    self.lang = config['Config']['lang']
    self.messages = messages
  
  def get(self, string):
    keys = string.split('.')
    message = self.messages
    for k in keys:
      message = message.get(k)
    return message.get(self.lang)
