# Metadatos
__author__ = 'Daniel Fernando Aguado Huaccharaqui'
__copyright__ = 'danielgis'
__credits__ = ['Daniel Aguado H.']
__version__ = '1.0.0'
__mail__ = 'daniel030891@gmail.com'

# Importamos librerias
import arcpy
import sys

# Solo se ejecuta si el archivo actual es ejecutado
# No se ejecuta si es importado
if __name__ == '__main__':
    try:
        # Declarando variables
        # Feature que recibira los nuevos atributos
        target_feature = arcpy.GetParameterAsText(0)
        # Feature que aportara los nuevos atributos
        join_feature = arcpy.GetParameterAsText(1)
        # Lista de campos que se desean considerar
        fields_selected = arcpy.GetParameterAsText(2)

        fields_selected = fields_selected.split(';')

        # Obtenemos las propiedades de los campos que fueron considerados
        fields_selected_properties = list(filter(lambda i: i.name in fields_selected, arcpy.ListFields(join_feature)))
        # Creamos un diccionario que tiene como clave el nombre del campo seleccionado y como value el objeto field
        # fields_selected_properties_dict = {i.name: i for i in fields_selected_properties}

        # Obtenemos todos los campos del target_feature
        target_feature_all_fields_name = list(map(lambda i: i.name, arcpy.ListFields(target_feature) ))

        # Creamos la variable field_analysis
        # Se agrega el campo SHAPE@ que hace referencia a la geometria del join_feature
        fields_analysis = ["SHAPE@"]
        # Agregamos a field_analysis los campos seleccionados
        fields_analysis.extend(fields_selected)

        # Creacion de campos seleccionados en el target_feature
        for field in fields_selected_properties:
            if field.name not in target_feature_all_fields_name:
                # Si el campo no existe en el target_feature, se crea
                arcpy.AddField_management(target_feature, field.name, field.type)
            else:
                # Si el campo ya existe en el target_feature se notifica
                arcpy.AddMessage(f'El campo {field.name} ya existe')
            
        # Creamos un FeatureLayer en memoria del target_feature
        target_feature_mfl = arcpy.MakeFeatureLayer_management(target_feature, 'target_feature_mfl')

        # Creamos un cursor para iterar todos los registros del join_feature
        with arcpy.da.SearchCursor(join_feature, fields_analysis) as cursor_sc:
            for row_sc in cursor_sc:
                # Realizamos una seleccion por localizacion para encontrar todos los registros de target_feature que se
                # intersectan con la geometria de join_feature en la iteracion
                arcpy.SelectLayerByLocation_management(target_feature_mfl, "INTERSECT", row_sc[0], "#", "NEW_SELECTION")
                
                # Realizamos un conteo de los elementos encontrado 
                target_feature_mfl_count = arcpy.GetCount_management(target_feature_mfl).getOutput(0)

                if int(target_feature_mfl_count):
                    # Si se encontraron datos, pasamos los atributos del join_feature al target_feature
                    with arcpy.da.UpdateCursor(target_feature_mfl, fields_analysis) as cursor_uc:
                        for row_uc in cursor_uc:
                            for field in fields_analysis[1:]:
                                row_uc[fields_analysis.index(field)] = row_sc[fields_analysis.index(field)]
                            cursor_uc.updateRow(row_uc)
                        del cursor_uc
            del cursor_sc

        # Al finalizar el proceso limpiamos la seleccion
        arcpy.SelectLayerByAttribute_management(target_feature_mfl, "CLEAR_SELECTION")

        # Retornamos el target_feature
        arcpy.SetParameterAsText(3, target_feature)
    except Exception:
        # En caso de error
        # Capturamos la excepcion
        e = sys.exc_info()[1]
        # Notificamos el error
        arcpy.AddError(e.args[0])
