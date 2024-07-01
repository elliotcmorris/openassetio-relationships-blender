import bpy
from openassetio.errors import BatchElementException
from openassetio.access import ResolveAccess
from openassetio.hostApi import HostInterface, ManagerFactory
from openassetio.errors import ConfigurationException
from openassetio.log import ConsoleLogger, SeverityFilter
from openassetio.pluginSystem import PythonPluginSystemManagerImplementationFactory
from openassetio_mediacreation.traits.content import LocatableContentTrait
from openassetio_mediacreation.traits.identity import DisplayNameTrait

class BlenderHostInterface(HostInterface):
    def identifier(self):
        return "org.blender.importplugin"

    def displayName(self):
        return "Blender Basic Import"

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

class OpenAssetIOFieldProps(bpy.types.PropertyGroup):
    entityRefStr: bpy.props.StringProperty(default="")
    

class ImportEntityReference(bpy.types.Operator):

    bl_idname = "object.import_openassetio_entityreference"
    bl_label = "Import EntityReference"

    def select_type_and_load(self, entityReference, displayName, path, mimetype):
        # Bit weird, the interface for blender is like `bpy.ops.import_scene.fbx`.
        # Wont always work, good enough for a prototype though.
        import_func = getattr(bpy.ops.import_scene, mimetype)
        import_func( filepath = path)
        
        # Assume the imported object is the active object
        imported_object = bpy.context.selected_objects[0] 
        imported_object["entity_reference"] = str(entityReference)
        imported_object.name = displayName
    
    def execute(self, context):
        entity_reference_input = context.scene.OpenAssetIOFieldProps.entityRefStr
        entity_reference = manager.createEntityReference(entity_reference_input)
        print("Resolving with ", entity_reference)
 
        context = manager.createContext()
        trait_set = set({LocatableContentTrait.kId, DisplayNameTrait.kId})
        traits_data = manager.resolve(entity_reference, trait_set, ResolveAccess.kRead, context)
        location = LocatableContentTrait(traits_data)
        displayName = DisplayNameTrait(traits_data)
        self.select_type_and_load(entity_reference, displayName.getName(), location.getLocation(), location.getMimeType())
        return {'FINISHED'}

class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "OpenAssetIO Import"
    bl_idname = "SCENE_PT_openassetioimport"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        openassetioInputFieldProps = bpy.context.scene.OpenAssetIOFieldProps
        
        row = layout.row()
        layout.label(text=f"Connected to : {manager.displayName()}")

        # Create an row where the buttons are aligned to each other.
        layout.label(text="EntityReference:")
        row = layout.row()
        row.prop(openassetioInputFieldProps, "entityRefStr", text="")

        # Big render button
        row = layout.row()
        row.scale_y = 3.0
        row.operator("object.import_openassetio_entityreference")
        
        if errorStr:
            row = layout.row()
            layout.label(text=f"Error: {errorStr}")

def register():
    bpy.utils.register_class(LayoutDemoPanel)
    bpy.utils.register_class(OpenAssetIOFieldProps)
    bpy.utils.register_class(ImportEntityReference)
    bpy.types.Scene.OpenAssetIOFieldProps = bpy.props.PointerProperty(type=OpenAssetIOFieldProps)


def unregister():
    bpy.utils.unregister_class(LayoutDemoPanel)
    bpy.utils.unregister_class(OpenAssetIOFieldProps)
    bpy.utils.unregister_class(ImportEntityReference)
    del(bpy.types.Scene.OpenAssetIOFieldProps)


if __name__ == "__main__":
    register()
