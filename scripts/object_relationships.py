import bpy
from openassetio.errors import BatchElementException
from openassetio.access import ResolveAccess, RelationsAccess
from openassetio.hostApi import HostInterface, ManagerFactory
from openassetio.errors import ConfigurationException
from openassetio.log import ConsoleLogger, SeverityFilter
from openassetio.trait import TraitsData
from openassetio.pluginSystem import PythonPluginSystemManagerImplementationFactory
from openassetio_mediacreation.traits.content import LocatableContentTrait
from openassetio_mediacreation.traits.representation import ProxyTrait, OriginalTrait

class BlenderHostInterface(HostInterface):
    def identifier(self):
        return "org.blender.relationshipPlugin"

    def displayName(self):
        return "Blender Basic Relationships"

errorStr = ""

logger = SeverityFilter(ConsoleLogger())
impl_factory = PythonPluginSystemManagerImplementationFactory(logger)
host_interface = BlenderHostInterface()

manager = ManagerFactory.defaultManagerForInterface(host_interface, impl_factory, logger)
 
if not manager:
    errorStr = (
        "No default manager configured, "
        f"check ${ManagerFactory.kDefaultManagerConfigEnvVarName}"
    )

if not manager.hasCapability(manager.Capability.kResolution):
    errorStr = (
        f"The manager '{manager.identifier()}' does not support entity resolution"
    )



class RelationshipProperties(bpy.types.PropertyGroup):
    
    my_string : bpy.props.StringProperty(name= "Enter Text")
    
    my_float_vector : bpy.props.FloatVectorProperty(name= "Scale", soft_min= 0, soft_max= 1000, default= (1,1,1))
    
    def get_proxies(self, context):
        
        entity_reference_str = bpy.context.active_object["entity_reference"]
        entity_reference = manager.createEntityReference(entity_reference_str)
        oaioContext = manager.createContext()
        
        proxy_relationship_pager = manager.getWithRelationship(entity_reference, TraitsData({ProxyTrait.kId}),10,RelationsAccess.kRead,oaioContext,set())
        original_relationship_pager = manager.getWithRelationship(entity_reference, TraitsData({OriginalTrait.kId}),10,RelationsAccess.kRead,oaioContext,set())
        

        #Assume no more than 10 proxies for this demo
        entity_references = proxy_relationship_pager.get()
        original_entity_references = original_relationship_pager.get() #Why would there be more than one of these? Interesting
        original_entity_str_set = [str(ref) for ref in original_entity_references]
        
        return [
            (str(entity_ref), str(entity_ref) + " (Original)" if str(entity_ref) in original_entity_str_set else str(entity_ref), "") for i, entity_ref in enumerate(entity_references)
        ]

    
    my_enum : bpy.props.EnumProperty(
        name= "Related Proxies",
        description= "Entities related to this entity by the proxy relationship.",
        items=get_proxies
    )

class SwapMeshDataToProxy(bpy.types.Operator):

    bl_idname = "object.relationship_swap_proxy"
    bl_label = "Replace with Proxy"
    

    def select_type_and_load(self, entityReference, path, mimetype, matrix):
        # Bit weird, the interface for blender is like `bpy.ops.import_scene.fbx`.
        # Wont always work, good enough for a prototype though.
        import_func = getattr(bpy.ops.import_scene, mimetype)
        import_func( filepath = path)
        
        # Assume the imported object are selected. Bit of a behaviour specific hack
        # Only one object comes in for this demo so don't think too hard about it.
        imported_objects = bpy.context.selected_objects
        for imported in imported_objects:
            imported.matrix_world = matrix
            imported["entity_reference"] = str(entityReference)
    
    def execute(self, context):
        mytool = bpy.context.scene.relations_tool
        entity_reference_input = mytool.my_enum
        entity_reference = manager.createEntityReference(entity_reference_input)
        print("Resolving with ", entity_reference)
 
        context = manager.createContext()
        trait_set = set({LocatableContentTrait.kId})
        traits_data = manager.resolve(entity_reference, trait_set, ResolveAccess.kRead, context)
        location = LocatableContentTrait(traits_data)
        print(location.getLocation())
        print(location.getMimeType())
        
        #Delete old object. It's inherently selected to be running this script from the panel
        this_object = bpy.context.active_object
        matrix = this_object.matrix_world.copy()
        bpy.ops.object.delete()

        #Load new object
        self.select_type_and_load(entity_reference, location.getLocation(), location.getMimeType(), matrix)
        
        return {'FINISHED'}


class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "OpenAssetIO Proxy Replacer"
    bl_idname = "SCENE_PT_openassetiorelationship"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        
        scene = bpy.context.scene        
        relationsTool = scene.relations_tool

        row = layout.row()
        layout.label(text=f"Connected to : {manager.displayName()}")

        # Create an row where the buttons are aligned to each other.
        imported_object = bpy.context.active_object
        stored_entity_ref = imported_object["entity_reference"]
        layout.label(text=f"EntityReference: {stored_entity_ref}")
        
        # Select proxy
        row = layout.row()
        layout.prop(relationsTool, "my_enum")
        
        # Big button
        row = layout.row()
        row.scale_y = 3.0
        row.operator("object.relationship_swap_proxy")
        
        if errorStr:
            row = layout.row()
            layout.label(text=f"Error: {errorStr}")

def register():
    bpy.utils.register_class(LayoutDemoPanel)
    bpy.utils.register_class(SwapMeshDataToProxy)
    bpy.utils.register_class(RelationshipProperties)
    bpy.types.Scene.relations_tool = bpy.props.PointerProperty(type= RelationshipProperties)


def unregister():
    bpy.utils.unregister_class(LayoutDemoPanel)
    bpy.utils.unregister_class(SwapMeshDataToProxy)
    bpy.utils.unregister_class(RelationshipProperties)
    del bpy.types.Scene.relations_tool


if __name__ == "__main__":
    register()
