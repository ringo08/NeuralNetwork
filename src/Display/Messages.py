
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
  },
  'dialog': {
    'title': {
      'create': {
        'network': {
          'en': 'create network',
          'ja': 'ネットワーク作成'
        }
      },
      'select': {
        'learningData': {
          'en': 'select a file for learning data to be loaded',
          'ja': '読み込む学習データ用ファイルを選択する'
        }
      },
      'save': {
        'network': {
          'en': 'Network save as',
          'ja': 'ネットワークの名前をつけて保存する'
        },
        'network': {
          'en': 'Network save as',
          'ja': 'ネットワークの名前をつけて保存する'
        }
      }
    },
    'message': {
      'network': {
        'overwrite': {
          'en': 'save network before overwrite?',
          'ja': '上書き前に保存しますか?'
        },
        'close': {
          'en': 'save network before close?',
          'ja': '閉じる前にネットワークを保存しますか?'
        }
      }
    }
  }
}

class Messages:
  def __init__(self, config=None):
    self.lang = config['Config']['lang'] if config else 'en'
    self.messages = messages

  def get(self, string):
    keys = string.split('.')
    message = self.messages
    for k in keys:
      message = message.get(k)
    return message.get(self.lang)
