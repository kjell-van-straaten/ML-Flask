class User:
  def __init__(self, id, username, password, role):
    self.id = id
    self.username = username
    self.password = password
    self.roles = self.generate_roles(role)

  def __repr__(self):
    return f'<User: {self.username}>'

  def generate_roles(self, role):
    roles = {'admin': False, 'config': False, 'view': False}

    if role == 'admin':
      roles['admin'] = True
      roles['config'] = True
      roles['view'] = True

    return roles

