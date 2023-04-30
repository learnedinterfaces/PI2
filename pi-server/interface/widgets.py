import math
from .costpreference import *
from difftree.schema import *
from .interaction import *
from .chars import char_sizes
from difftree.nodes import *

MAX_LABEL_WIDTH = 500

def str_width(s):
  return sum([char_sizes[c]['width'] for c in s])

def str_height(s, max_width=MAX_LABEL_WIDTH):
  width = str_width(s)
  return math.ceil(width / max_width) * 20

def h_options_width(node_children, max_width=MAX_LABEL_WIDTH, padding=15):
  """
  Computes expected width of horizontal options list (radio, checkbox)
  """
  width = 0
  for child in node_children:
    if not isinstance(child, str):
      child = child.get_text()
    width += min(str_width(child), max_width)
  width += len(node_children) * padding + 20 * len(node_children)
  return width


def h_options_height(node_children, max_width=MAX_LABEL_WIDTH, padding=15):
  """
  Computes expected width of horizontal options list (radio, checkbox)
  """
  heights = []
  for child in node_children:
    if not isinstance(child, str):
      child = child.get_text()
    heights.append(str_height(child, max_width))
  return (max(heights) or 10) + padding

def v_options_width(node_children, max_width=MAX_LABEL_WIDTH, padding=20):
  widths = []
  for child in node_children:
    if not isinstance(child, str):
      child = child.get_text()
    text_width = str_width(child)
    widths.append(min(text_width, max_width) + padding)
  return max(widths) or 15

def v_options_height(node_children, max_width=MAX_LABEL_WIDTH, padding=5):
  height = 0
  for child in node_children:
    if not isinstance(child, str):
      child = child.get_text()
    height += str_height(child, max_width) + padding
  return height

def leaf_children(node):
  """
  Radio and Checkbox widgets only consider child nodes that are leaves (text)
  """
  if hasattr(node.node_schema, "node"):
    return ['' if c.node_schema else c for c in node.node_schema.node.children]
  else:
    return ['' if c.node_schema else c 
        for c in node.node_schema.schema_list[0].node.children]


class Layout(object):

    view_id = 0

    def next_id(self):
        _id = Layout.view_id
        Layout.view_id += 1
        return 'w' + str(_id)

    def next_iid(self):
        iid = Interaction.interact_id
        Interaction.interact_id += 1
        return 'i' + str(iid)

    def __init__(self):
        self.vid = self.next_id()

class Vertical(Layout):

    def __init__(self, children, widget=None):
        super(Vertical, self).__init__()
        self.children = children

        self.widget = widget # the layout node itself may refer to a widget


        self.x = 0
        self.y = 0

        self.update_size()

    def wtype(self):
        return 'Vertical'

    def update_size(self):
        if self.widget is None:
            self.width = max([c.width for c in self.children])
            self.height = sum([c.height + 20 for c in self.children])

        else:
            self.width = max([(self.widget.width + c.width) for c in self.children])
            self.height = sum([max( self.widget.height, c.height) + 20 for c in self.children])

    def push_xy(self, x, y):
        self.x = x
        self.y = y
        if self.widget:
            self.widget.push_xy(x, y)
        for c in self.children:
            if self.widget:
                c.push_xy(x + self.widget.width, y)
            else:
                c.push_xy(x, y)
            y += max(c.height, 0 if self.widget is None else self.widget.height)

    def layout_to_spec(self):
        spec = {}
        spec["id"] = str(self.vid)
        if self.widget is not None:
            spec["widget"] = self.widget.layout_to_spec()
        spec["width"] = self.width
        spec["height"] = self.height
        spec["children"] = [c.layout_to_spec() for c in self.children]
        spec["type"] = "VLayout"
        return spec

class Horizontal(Layout):

    def __init__(self, children, widget=None):
        super(Horizontal, self).__init__()
        self.children = children

        self.widget = widget # the layout node itself may refer to a widget


        self.x = 0
        self.y = 0

        self.update_size()

    def wtype(self):
        return "Horizontal"

    def update_size(self):
        if self.widget is None:
            self.width = sum([c.width + 20 for c in self.children])
            self.height = max([c.height for c in self.children])
        else:
            self.width = sum([self.widget.width + c.width + 20 for c in self.children])
            self.height = max([max(self.widget.height, c.height) for c in self.children])

    def push_xy(self, x, y):
        self.x = x
        self.y = y

        if self.widget:
            self.widget.push_xy(x, y)

        x += (0 if self.widget is None else self.widget.width)
        for c in self.children:
            c.push_xy(x, y)
            x += c.width + (0 if self.widget is None else self.widget.width)

    def layout_to_spec(self):
        spec = {}
        spec["id"] = str(self.vid)
        if self.widget is not None:
            spec["widget"] = self.widget.layout_to_spec()
        spec["width"] = self.width
        spec["height"] = self.height
        spec["children"] = [c.layout_to_spec() for c in self.children]
        spec["type"] = "HLayout"
        return spec

class Widget(Layout):

    def __init__(self, node):
        super(Widget, self).__init__()
        self.node = node
        if not isinstance(node, str):
            node.widget = self
        self.x = 0
        self.y = 0

    def push_xy(self, x, y):
        self.x = x
        self.y = y

    def layout_to_spec(self):
        spec = {}
        spec["id"] = str(self.vid)
        spec["width"] = self.width
        spec["height"] = self.height
        spec["type"] = "ref"
        spec["ref"] = str(self.vid)
        spec["name"] = self.wtype()
        return spec

class Radio(Widget):

    max_num = 30

    @classmethod
    def support(cls, node):
        if node.node_schema is None: return False
        return isinstance(node.node_schema, TypeSchema)

    def wtype(self):
        return "radio"

    def cost(self):
        node = self.node.node_schema.node
        x = len(node.children)
        if x > self.max_num:
            return float("inf")
        for c in node.children:
            if c.node_schema is None and len(c.get_text()) > 30: return 30000 + len(c.get_text()) ** 2
        return 143 + 162 * x + len(node.get_text())

    @property
    def width(self):
        pass

    @property
    def height(self):
        pass

    def to_spec(self):
        spec = {}
        spec["id"] = str(self.vid)
        spec["type"] = "Radio"
        spec["data"] = []
        for i, c in enumerate(self.node.node_schema.node.children):
            spec["data"].append({"label": c.get_text() if c.node_schema is None else "", "value": i})
        spec['width'] = self.width
        spec['height'] = self.height
        return spec

    def get_text(self):
        labels = []
        for i, c in enumerate(self.node.node_schema.node.children):
            labels.append(c.get_text())
        return "Radio(" + "|".join(labels) + ")"

    def interaction_to_spec(self):
        spec = {}

        spec["id"] = str(self.next_iid())
        spec["source"] = str(self.vid)
        spec["target"] = str(self.node.node_schema.node.difftree.vis.vid)
        spec["m"] = {"type": "SINGLE", "space": "mark"}
        spec["h"] = {str(self.node.node_schema.node.nid): "value"}

        return [spec]

class HRadio(Radio):

  def wtype(self):
      return "hradio"

  @property
  def width(self):
    return h_options_width(leaf_children(self.node), padding=30)

  @property
  def height(self):
    return h_options_height(leaf_children(self.node))

  def to_spec(self):
    spec = super(HRadio, self).to_spec()
    spec["orientation"] = "H"
    return spec

  def get_text(self):
    labels = []
    for c in self.node.node_schema.node.children:
      labels.append(c.get_text())
    return "HRadio(" + "|".join(labels) + ")"

class VRadio(Radio):
  def wtype(self):
      return "vradio"

  @property
  def width(self):
    return v_options_width(leaf_children(self.node), padding=40)

  @property
  def height(self):
    return v_options_height(leaf_children(self.node), padding=10)

  def to_spec(self):
    spec = super(VRadio, self).to_spec()
    spec["orientation"] = "V"
    return spec

  def get_text(self):
    labels = []
    for c in self.node.node_schema.node.children:
      labels.append(c.get_text())
    return "VRadio(" + "|".join(labels) + ")"

class CRadio(Widget):

    max_num = 30

    @classmethod
    def support(cls, node):
        if node.node_schema is None: return False
        return isinstance(node.node_schema, OrSchema)

    def wtype(self):
        return "radio"

    def cost(self):
        node = self.node.node_schema.node
        x = len(node.children)
        if x > self.max_num:
            return float("inf")
        for c in node.children:
            if c.node_schema is None and len(c.get_text()) > 30: return 30000 + len(c.get_text()) ** 2
        return 143 + 162 * x + len(node.children) * 10

    @property
    def width(self):
        return 50

    @property
    def height(self):
        return 50

    def to_spec(self):
        spec = {}
        spec["id"] = str(self.vid)
        spec["type"] = "Radio"
        spec["data"] = []
        for i, c in enumerate(self.node.node_schema.node.children):
          spec['data'].append(dict( label="", value=i))
          #spec["data"].append({"label": c.get_text() if c.node_schema is None else "", "value": i})
        spec['width'] = self.width
        spec['height'] = self.height
        return spec

    def get_text(self):
        labels = []
        for i, c in enumerate(self.node.node_schema.node.children):
            labels.append(c.get_text())
        return "Radio(" + "|".join(labels) + ")"

    def interaction_to_spec(self):
        spec = {}

        spec["id"] = str(self.next_iid())
        spec["source"] = str(self.vid)
        spec["target"] = str(self.node.node_schema.node.difftree.vis.vid)
        spec["m"] = {"type": "SINGLE", "space": "mark"}
        spec["h"] = {str(self.node.node_schema.node.nid): "value"}

        return [spec]

class Button(Widget):
    max_width = 90
    max_num = 50

    @classmethod
    def support(cls, node):
        if node.node_schema is None: return False
        return isinstance(node.node_schema, TypeSchema)

    def wtype(self):
        return "button"

    def cost(self):
        node = self.node.node_schema.node
        x = len(node.children)
        if x > self.max_num:
            return float("inf")
        for c in node.children:
            if len(c.get_text()) > 30: 
                return 30000  + len(c.get_text()) ** 2
        return 140 + 162 * x + len(node.get_text())

    @property
    def width(self):
        return h_options_width(leaf_children(self.node), self.max_width, padding=16)

    @property
    def height(self):
        return h_options_height(leaf_children(self.node), self.max_width, padding=16)

    def to_spec(self):
        spec = {}

        spec["id"] = str(self.vid)
        spec["type"] = "Button"
        spec["data"] = []
        for i, c in enumerate(self.node.node_schema.node.children):
            spec["data"].append({"label": c.get_text(), "value": i})
        return spec

    def get_text(self):
        labels = []
        for i, c in enumerate(self.node.node_schema.node.children):
            labels.append(c.get_text())
        return "Button(" + "|".join(labels) + ")"

    def interaction_to_spec(self):
        spec = {}

        spec["id"] = str(self.next_iid())
        spec["source"] = str(self.vid)
        spec["target"] = str(self.node.node_schema.node.difftree.vis.vid)
        spec["m"] = {"type": "SINGLE", "space": "mark"}
        spec["h"] = {str(self.node.node_schema.node.nid): "value"}

        return [spec]

class Toggle(Widget):

    @classmethod
    def support(cls, node):
        if node.node_schema is None: return False

        return isinstance(node.node_schema, OptionSchema)

    def wtype(self):
        return "toggle"

    def cost(self):
        return 100

    @property
    def width(self):
        return 50

    @property
    def height(self):
        return 30

    def to_spec(self):
        spec = {}

        spec["id"] = str(self.vid)
        spec["type"] = "Toggle"
        return spec

    def get_text(self):
        labels = []
        for i, c in enumerate(self.node.node_schema.node.children):
            labels.append(c.get_text())
        return "Toggle"

    def interaction_to_spec(self):
        spec = {}

        spec["id"] = str(self.next_iid())
        spec["source"] = str(self.vid)
        spec["target"] = str(self.node.node_schema.node.difftree.vis.vid)
        spec["m"] = {"type": "SINGLE", "space": "mark"}
        spec["h"] = {}
        spec['h'][str(self.node.node_schema.node.nid)] = "value"
        tmp = self.node.node_schema
        while(isinstance(tmp.sub_schema, OptionSchema)) and\
            (isinstance(tmp.node.children[0], (OPTNode, CoOPTNode))):
            spec['h'][str(tmp.sub_schema.node.nid)] = "value"
            tmp = tmp.sub_schema
        return [spec]

class Slider(Widget):

    schema = TypeSchema(Type(EType.NUMBER))

    @classmethod
    def support(cls, node):
        if node.node_schema is None: return False
        if not cls.schema.compatible(node.node_schema): return False
        try:
            [int(c.get_text()) for c in node.node_schema.node.children]
        except:
            return False
        return True

    def wtype(self):
        return "slider"

    def cost(self):
        return 570

    @property
    def width(self):
        return 130

    @property
    def height(self):
        return 20 + 20

    def min_value(self):
        return min([int(c.get_text()) for c in self.node.node_schema.node.children])

    def max_value(self):
        return max([int(c.get_text()) for c in self.node.node_schema.node.children])

    def to_spec(self):
        spec = {}

        spec["id"] = str(self.vid)
        spec["type"] = "Slider"
        spec["data"] = {"min": self.min_value(), "max": self.max_value()}
        return spec

    def get_text(self):
        return "Slider(" + str(self.min_value()) + "," + str(self.max_value()) + ")"

    def interaction_to_spec(self):
        spec = {}

        spec["id"] = str(self.next_iid())
        spec["source"] = str(self.vid)
        spec["target"] = str(self.node.node_schema.node.difftree.vis.vid)
        spec["m"] = {"type": "SINGLE", "space": "mark"}
        spec["h"] = {str(self.node.node_schema.node.nid): "value"}

        return [spec]

class Checkbox(Widget):

    max_num = 10

    @classmethod
    #[opt(T), opt(T), opt(T)]
    def support(cls, node):
        if node.node_schema is None: return False
        if isinstance(node.node_schema, ListSchema):
            for i in node.node_schema.schema_list:
                if not (isinstance(i, OptionSchema) and isinstance(i.sub_schema, TypeSchema)):
                    return False
            return True
        else:
            return False

    def wtype(self):
        return "checkbox"

    def cost(self):
        x = len(self.node.node_schema.schema_list)
        if x > self.max_num:
            return float("inf")
        for c in self.node.node_schema.schema_list[0].node.children:
            if len(c.get_text()) > 20: return 30000  + len(c.get_text()) ** 2
        return 30 + 5 * x * x + len(self.node.node_schema.schema_list[0].node.get_text()) * 10

    @property
    def width(self):
      raise Exception("Checkbox.width not implemented. See HCheckbox and VCheckbox")

    @property
    def height(self):
      raise Exception("Checkbox.height not implemented. See HCheckbox and VCheckbox")

    def to_spec(self):
        spec = {}

        spec["id"] = str(self.vid)
        spec["type"] = "Checkbox"
        spec["data"] = []
        for i, c in enumerate(self.node.node_schema.schema_list[0].node.children):
            spec["data"].append({"label": c.get_text(), "value": i})
        spec['width'] = self.width
        spec['height'] = self.height
        return spec

    def get_text(self):
        labels = []
        for i, c in enumerate(self.node.node_schema.schema_list[0].node.children):
            labels.append(c.get_text())
        return "Checkbox(" + "|".join(labels) + ")"

    def interaction_to_spec(self):
        spec = {}

        spec["id"] = str(self.next_iid())
        spec["source"] = str(self.vid)
        spec["target"] = str(self.node.node_schema.schema_list[0].node.difftree.vis.vid)
        spec["m"] = {"type": "SINGLE", "space": "mark"}
        spec["h"] = {str(self.node.node_schema.schema_list[0].node.nid): "value"}

        return [spec]

class HCheckbox(Checkbox):
  def wtype(self):
    return "hcheckbox"

  @property
  def width(self):
    return h_options_width(leaf_children(self.node))

  @property
  def height(self):
    return h_options_height(leaf_children(self.node))

  def to_spec(self):
    spec = super(HCheckbox, self).to_spec()
    spec["orientation"] = "H"
    return spec

  def get_text(self):
    labels = []
    for c in self.node.node_schema.schema_list[0].node.children:
      labels.append(c.get_text())
    return "HCheck(" + "|".join(labels) + ")"

class VCheckbox(Checkbox):
  def wtype(self):
    return "vcheckbox"

  @property
  def width(self):
    return v_options_width(leaf_children(self.node))

  @property
  def height(self):
    return v_options_height(leaf_children(self.node))

  def to_spec(self):
    spec = super(VCheckbox, self).to_spec()
    spec["orientation"] = "V"
    return spec

  def get_text(self):
    labels = []
    for c in self.node.node_schema.schema_list[0].node.children:
      labels.append(c.get_text())
    return "VCheck(" + "|".join(labels) + ")"

class Dropdown(Widget):

    max_num = 100

    @classmethod
    def support(cls, node):
        if node.node_schema is None: return False
        return isinstance(node.node_schema, TypeSchema)

    def wtype(self):
        return "dropdown"

    def cost(self):
        node = self.node.node_schema.node
        x = len(node.children)
        if x > self.max_num:
            return float("inf")
        for c in node.children:
            if len(c.get_text()) > 30: return 30000  + len(c.get_text()) ** 2
        
        if PREFERDROPDOWN: return 0 
        return 276 + 125 * x + 0.07 * x * x + 0.5*len(node.get_text())
        #return  x + 0.07 * x * x + 0.5*len(node.get_text())

    @property
    def width(self):
      return v_options_width(
          self.node.node_schema.node.children, float('inf')) + 10

    @property
    def height(self):
        return 25

    def to_spec(self):
        spec = {}

        spec["id"] = str(self.vid)
        spec["type"] = "Dropdown"
        spec["data"] = []
        for i, c in enumerate(self.node.node_schema.node.children):
            spec["data"].append({"label": c.get_text(), "value": i})
        return spec

    def get_text(self):
        labels = []
        for i, c in enumerate(self.node.node_schema.node.children):
            labels.append(c.get_text())
        return "Dropdown(" + "|".join(labels) + ")"

    def interaction_to_spec(self):
        spec = {}

        spec["id"] = str(self.next_iid())
        spec["source"] = str(self.vid)
        spec["target"] = str(self.node.node_schema.node.difftree.vis.vid)
        spec["m"] = {"type": "SINGLE", "space": "mark"}
        spec["h"] = {str(self.node.node_schema.node.nid): "value"}

        return [spec]

class RangeSlider(Widget):

    schema = ListSchema([TypeSchema(Type(EType.NUMBER)), TypeSchema(Type(EType.NUMBER))])

    @classmethod
    def support(cls, node):
        if node.node_schema is None: return False
        if not cls.schema.compatible(node.node_schema): return False
        try:
            [float(c.get_text()) for c in node.node_schema.schema_list[0].node.children]
            [float(c.get_text()) for c in node.node_schema.schema_list[1].node.children]
        except:
            return False
        return True

    def wtype(self):
        return "rangeslider"

    def cost(self):
        return 100

    @property
    def width(self):
        return 300

    @property
    def height(self):
        return 120

    def min_value(self):
        return min([float(c.get_text()) for c in self.node.node_schema.schema_list[0].node.children])

    def max_value(self):
        return max([float(c.get_text()) for c in self.node.node_schema.schema_list[1].node.children])

    def to_spec(self):
        spec = {}

        spec["id"] = str(self.vid)
        spec["type"] = "RangeSlider"
        spec["data"] = {"min": self.min_value(), "max": self.max_value()}
        return spec

    def get_text(self):
        return "RangeSlider(" + str(self.min_value()) + "," + str(self.max_value()) + ")"

    def interaction_to_spec(self):
        spec = {}

        spec["id"] = str(self.next_iid())
        spec["source"] = str(self.vid)
        spec["target"] = str(self.node.node_schema.schema_list[0].node.difftree.vis.vid)
        spec["m"] = {"type": "SINGLE", "space": "mark"}
        spec["h"] = {str(self.node.node_schema.schema_list[0].node.nid): "left",
                     str(self.node.node_schema.schema_list[1].node.nid): "right"}

        return [spec]

class Adder(Widget):
    @classmethod
    def support(cls, node):
        if node.node_schema is None: return False
        return isinstance(node.node_schema, StarSchema)

    def wtype(self):
        return "adder"

    def cost(self):
        return 30000

    @property
    def width(self):
        return 50

    @property
    def height(self):
        return 50

    def to_spec(self):
        spec = {}

        spec["id"] = str(self.vid)
        spec["type"] = "Adder"
        return spec

    def get_text(self):
        return "Adder"

    def interaction_to_spec(self):
        return []

class Textbox(Widget):

    schema = TypeSchema(Type(EType.STRING))

    @classmethod
    def support(cls, node):
        if node.node_schema is None: return False
        return cls.schema.compatible(node.node_schema)

    def wtype(self):
        return "textbox"

    def cost(self):
        return 4790

    @property
    def width(self):
        return 100

    @property
    def height(self):
        return 25

    def to_spec(self):
        spec = {}

        spec["id"] = str(self.vid)
        spec["type"] = "Textbox"
        return spec

    def get_text(self):
        return "Textbox"

    def interaction_to_spec(self):
        spec = {}

        spec["id"] = str(self.next_iid())
        spec["source"] = str(self.vid)
        spec["target"] = str(self.node.node_schema.node.difftree.vis.vid)
        spec["m"] = {"type": "SINGLE", "space": "mark"}
        spec["h"] = {str(self.node.node_schema.node.nid): "text"}

        return [spec]

class Label(Widget):

    def wtype(self):
        return "Label"

    @property
    def width(self):
        if self.node == 'Interaction':
            return h_options_width([self.node])
        else:
            return h_options_width([self.get_text()])

    @property
    def height(self):
        if self.node == 'Interaction':
            return h_options_height([self.node])
        else:
            return h_options_height([self.get_text()])

    def to_spec(self):
        spec = super(Widget, self).to_spec()
        return spec

    def get_text(self):
        return self.node.get_text()

    def layout_to_spec(self):
        spec = {}
        spec["id"] = str(self.vid)
        spec["width"] = self.width
        spec["height"] = self.height
        spec["type"] = "Label"
        if self.node == 'Interaction':
            spec["data"] = self.node
        else:
            spec["data"] = self.get_text()
        spec["name"] = self.wtype()
        return spec

Widgets = [
    #HRadio,
    #VRadio,
    CRadio,
    Button,
    Toggle,
    Slider,
    HCheckbox,
    VCheckbox,
    Dropdown,
    RangeSlider,
    Adder,
    #Textbox,
]


def candidate_widgets(node):
    candidates = []
    for w in Widgets:
        if w.support(node):
            candidates.append(w)
    return candidates


class Unknown(Layout):

    def __init__(self, children, widget=None):
        self.children = children
        self.widget = widget
        self.update_size()

    def update_size(self):
        self.width = max([c.width + (0 if self.widget is None else self.widget.width) for c in self.children])
        self.height = max([max(c.height, 0 if self.widget is None else self.widget.height) for c in self.children])

    def push_xy(self, x, y):
        self.x = x
        self.y = y
        for c in self.children:
            c.push_xy(x + (0 if self.widget is None else self.widget.width), y)

