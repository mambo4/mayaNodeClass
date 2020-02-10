import pymel.core as pm

ATTRIBUTE_DICT = {"name":"logan", "race":"human", "occupation":"TA", "foo":1, "qux":True, "baz":2.0, "instruments":["bass","guitar","harmonica"]}

TYPE_DICT={
    #todo: message attrs?
    float: 'double',
    int: 'long',
    bool: 'bool',
    str: 'string',
    unicode: 'string',
    list: 'enum',
}


def test_node():
    node = pm.createNode("network", name="TestNode")
    for attribute,value in ATTRIBUTE_DICT.iteritems():
        type=value.__class__
        maya_type=TYPE_DICT[type]
        if maya_type=="enum":
            print "{}({}) is enum".format(attribute,value)
            pm.addAttr(node, longName=attribute, type=maya_type, enumName=value)
        else:
            pm.addAttr(node,longName=attribute,type=maya_type)
            node.setAttr(attribute,value)
    return node


class MayaNodeClass(object):
    """
    a class to get and set custom maya node attributes
    when no node exists, get and set instance attributes
    """

    PYMEL_NODE_CLASS = pm.nodetypes.Network

    def __init__(self,**kwargs):

        self._node=kwargs.get("node",None)
        if self._node:
            self._node=pm.PyNode(self._node)
        self._attribute_list = kwargs.get("attribute_list",None)
        # todo implement creation with only _attribute_dict
        self._attribute_dict = kwargs.get("attribute_dict", None)
        self._load_attributes()

    def __str__(self):
        return("NodeClass")

    def _load_attributes(self):

        if self._node:
            self._attribute_list =[attribute.longName() for attribute in self._node.listAttr(ud=True)]
        self._build_attributes()


    def _build_attributes(self):
        """
        this adds all the attributes in self._attribute list, no values are populated.
        :return:
        """
        if self._attribute_list:
            for attribute_name in self._attribute_list:
                self._add_attribute(attribute_name)
        else:
            raise ValueError("{}._attribute_list is empty. unable to build attributes.".format(self))

    def _add_attribute(self,attribute_name):
        """
        an attribute factory. add <attribute_name> to self using @property decorators
        build setter that sets the maya node attr if node exists, always set private attr
        and getter that return the maya node attr value  if node exists

        and
        :param attribute_name:
        :return:
        """
        # private is needed to eliminate recursion error when self._node is not present
        private_attribute = "_" + attribute_name

        def _set(attribute_name, value):

            if self._node:
                self._node.setAttr(attribute_name, value)
                setattr(self, private_attribute, value)
            else:
                setattr(self, private_attribute, value)

        def _get(attribute_name):

            if self._node:
                return self._node.attr(attribute_name).get()
            else:
                getattr(self, private_attribute)

        # is there another way to add the property <attribute_name> ?
        self.__dict__[attribute_name] = property(_set, _get)
        setattr(self, attribute_name, _get(attribute_name))

    def _create_node(self):
        """
        if self._node does not exist, create it
        default maya node type is PYMEL_NODE_CLASS
        :return:
        """
        pass

    def info(self):
        if self._attribute_list:
            for attr in self._attribute_list:
                print "{}.{}:{}".format(self, attr, getattr(self,attr))

if __name__ == '__main__':
    try:
        pm.delete("TestNode")
    except:
        pass
    node=test_node()
    nc=MayaNodeClass(node="TestNode")
    nc.info()

