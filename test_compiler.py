#!/usr/bin/env python3
# test_compiler.py
# Pruebas automatizadas para el empaquetador automático de parches/traducciones

import unittest
from unittest.mock import MagicMock, patch
import os
import shutil
import zipfile
from pathlib import Path
import types

# Importar la app de compilación directamente
from Compiler_GUIV2 import MetalWarCompilerApp

class TestAutomaticPacker(unittest.TestCase):
    def setUp(self):
        # Guardar estado anterior de directorios/archivos si existen para no estropearlos
        self.old_dir_exists = Path("TRANSLATION_FILES_TO_PACK").exists()
        if self.old_dir_exists:
            self.temp_backup_dir = Path("TRANSLATION_FILES_TO_PACK_BACKUP_TEST")
            if self.temp_backup_dir.exists():
                shutil.rmtree(self.temp_backup_dir)
            shutil.move("TRANSLATION_FILES_TO_PACK", self.temp_backup_dir)

        self.old_packed_exists = Path("packed.dat").exists()
        if self.old_packed_exists:
            if Path("packed.dat.backup_test").exists():
                os.remove("packed.dat.backup_test")
            shutil.move("packed.dat", "packed.dat.backup_test")

        # Mockear las funciones de messagebox para evitar TclError de Tkinter en entornos sin DISPLAY
        self.patcher_showwarning = patch('tkinter.messagebox.showwarning')
        self.patcher_showerror = patch('tkinter.messagebox.showerror')
        self.mock_showwarning = self.patcher_showwarning.start()
        self.mock_showerror = self.patcher_showerror.start()

        # Crear una instancia simulada de la app (Mock)
        self.mock_app = MagicMock()
        # Enlazar el método _crear_packed_dat real al mock
        self.mock_app._crear_packed_dat = types.MethodType(
            MetalWarCompilerApp._crear_packed_dat, self.mock_app
        )

        # Simular los métodos de consola y callbacks de Tkinter after
        self.console_messages = []
        def escribir_en_consola(text, style=None):
            self.console_messages.append(text)
        self.mock_app.escribir_en_consola = escribir_en_consola

        # Cuando llame a self.after, ejecutamos el callback inmediatamente
        def after(ms, func):
            func()
        self.mock_app.after = after

        # Limpiar cualquier residuo de directorios de prueba
        if Path("TRANSLATION_FILES_TO_PACK").exists():
            shutil.rmtree("TRANSLATION_FILES_TO_PACK")
        Path("TRANSLATION_FILES_TO_PACK").mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        # Detener parches de messagebox
        self.patcher_showwarning.stop()
        self.patcher_showerror.stop()

        # Limpiar directorios creados en las pruebas
        if Path("TRANSLATION_FILES_TO_PACK").exists():
            shutil.rmtree("TRANSLATION_FILES_TO_PACK")

        if Path("packed.dat").exists():
            try:
                os.remove("packed.dat")
            except:
                pass

        if Path("packed.dat.tmp").exists():
            try:
                os.remove("packed.dat.tmp")
            except:
                pass

        # Restaurar estado original
        if self.old_dir_exists and Path("TRANSLATION_FILES_TO_PACK_BACKUP_TEST").exists():
            if Path("TRANSLATION_FILES_TO_PACK").exists():
                shutil.rmtree("TRANSLATION_FILES_TO_PACK")
            shutil.move("TRANSLATION_FILES_TO_PACK_BACKUP_TEST", "TRANSLATION_FILES_TO_PACK")

        if self.old_packed_exists and Path("packed.dat.backup_test").exists():
            if Path("packed.dat").exists():
                os.remove("packed.dat")
            shutil.move("packed.dat.backup_test", "packed.dat")

    def test_empty_folder_detection(self):
        """Verifica que una carpeta vacía (o solo con .gitkeep) detiene el proceso y no genera packed.dat"""
        # Crear .gitkeep en la carpeta vacía
        with open("TRANSLATION_FILES_TO_PACK/.gitkeep", "w", encoding="utf-8") as f:
            f.write("")

        # Ejecutar empaquetado
        result = self.mock_app._crear_packed_dat()

        # Debe retornar False
        self.assertFalse(result)
        # No debe existir packed.dat
        self.assertFalse(Path("packed.dat").exists())

        # Debe haber registrado un aviso de carpeta vacía en consola
        console_output = "".join(self.console_messages)
        self.assertIn("está vacía o solo contiene elementos excluidos", console_output)

        # Debe haber llamado a showwarning
        self.mock_showwarning.assert_called_once()

    def test_root_files_packing(self):
        """Verifica que los archivos en la raíz se empaquetan correctamente"""
        # Crear un archivo de prueba en la raíz de TRANSLATION_FILES_TO_PACK
        with open("TRANSLATION_FILES_TO_PACK/test1.txt", "w", encoding="utf-8") as f:
            f.write("contenido de prueba de root")

        # Ejecutar empaquetado
        result = self.mock_app._crear_packed_dat()

        self.assertTrue(result)
        self.assertTrue(Path("packed.dat").exists())

        # Verificar contenido del zip
        with zipfile.ZipFile("packed.dat", "r") as zip_f:
            namelist = zip_f.namelist()
            self.assertIn("test1.txt", namelist)
            self.assertEqual(zip_f.read("test1.txt").decode("utf-8"), "contenido de prueba de root")

    def test_recursive_packing_and_relative_paths(self):
        """Verifica el empaquetado recursivo de subdirectorios, la exclusión de .gitkeep y rutas relativas"""
        # Crear estructura de prueba
        os.makedirs("TRANSLATION_FILES_TO_PACK/Data", exist_ok=True)
        os.makedirs("TRANSLATION_FILES_TO_PACK/Text", exist_ok=True)

        with open("TRANSLATION_FILES_TO_PACK/Data/spanish.dat", "w", encoding="utf-8") as f:
            f.write("datos en espanol")
        with open("TRANSLATION_FILES_TO_PACK/Text/dialogue.txt", "w", encoding="utf-8") as f:
            f.write("hola mundo")
        with open("TRANSLATION_FILES_TO_PACK/Text/.gitkeep", "w", encoding="utf-8") as f:
            f.write("")
        with open("TRANSLATION_FILES_TO_PACK/readme.txt", "w", encoding="utf-8") as f:
            f.write("lee esto")

        # Ejecutar empaquetado
        result = self.mock_app._crear_packed_dat()

        self.assertTrue(result)
        self.assertTrue(Path("packed.dat").exists())

        # Verificar rutas relativas exactas y exclusiones
        with zipfile.ZipFile("packed.dat", "r") as zip_f:
            namelist = zip_f.namelist()

            # Deben estar las rutas relativas correctas
            self.assertIn("Data/spanish.dat", namelist)
            self.assertIn("Text/dialogue.txt", namelist)
            self.assertIn("readme.txt", namelist)

            # NO deben aparecer .gitkeep
            self.assertNotIn(".gitkeep", namelist)
            self.assertNotIn("Text/.gitkeep", namelist)

            # Verificar contenidos
            self.assertEqual(zip_f.read("Data/spanish.dat").decode("utf-8"), "datos en espanol")
            self.assertEqual(zip_f.read("Text/dialogue.txt").decode("utf-8"), "hola mundo")

    def test_exclusions(self):
        """Verifica que las cachés de Python y temporales se excluyen del empaquetado"""
        # Crear archivos de prueba
        os.makedirs("TRANSLATION_FILES_TO_PACK/__pycache__", exist_ok=True)
        with open("TRANSLATION_FILES_TO_PACK/__pycache__/module.pyc", "w") as f:
            f.write("compiled python")
        with open("TRANSLATION_FILES_TO_PACK/module.pyc", "w") as f:
            f.write("compiled python")
        with open("TRANSLATION_FILES_TO_PACK/test.tmp", "w") as f:
            f.write("temp file")
        with open("TRANSLATION_FILES_TO_PACK/~$doc.docx", "w") as f:
            f.write("office temp lock")
        with open("TRANSLATION_FILES_TO_PACK/valid.txt", "w") as f:
            f.write("keep this")

        # Ejecutar empaquetado
        result = self.mock_app._crear_packed_dat()

        self.assertTrue(result)

        # Verificar exclusiones en el ZIP
        with zipfile.ZipFile("packed.dat", "r") as zip_f:
            namelist = zip_f.namelist()
            self.assertIn("valid.txt", namelist)
            self.assertNotIn("module.pyc", namelist)
            self.assertNotIn("__pycache__/module.pyc", namelist)
            self.assertNotIn("test.tmp", namelist)
            self.assertNotIn("~$doc.docx", namelist)

    def test_safe_replacement_of_existing_packed_dat(self):
        """Verifica que si ya existe un packed.dat, se reemplaza únicamente al generar con éxito el nuevo"""
        # 1. Crear un packed.dat previo con contenido antiguo
        with zipfile.ZipFile("packed.dat", "w") as old_zip:
            old_zip.writestr("old_file.txt", "contenido viejo")

        # 2. Crear una estructura nueva válida en TRANSLATION_FILES_TO_PACK
        with open("TRANSLATION_FILES_TO_PACK/new_file.txt", "w", encoding="utf-8") as f:
            f.write("contenido nuevo")

        # 3. Ejecutar empaquetado
        result = self.mock_app._crear_packed_dat()

        self.assertTrue(result)

        # 4. Verificar que packed.dat contiene el nuevo archivo y ya no el antiguo
        with zipfile.ZipFile("packed.dat", "r") as zip_f:
            namelist = zip_f.namelist()
            self.assertIn("new_file.txt", namelist)
            self.assertNotIn("old_file.txt", namelist)

    def test_unreadable_file_handling(self):
        """Verifica que un archivo ilegible/error de lectura detiene el empaquetado, no altera packed.dat previo, y muestra un error"""
        # Crear un packed.dat previo
        with zipfile.ZipFile("packed.dat", "w") as old_zip:
            old_zip.writestr("old_file.txt", "contenido viejo")

        # Simular archivos empaquetables usando open real
        with open("TRANSLATION_FILES_TO_PACK/valid1.txt", "w") as f:
            f.write("contenido")

        # Forzar que la lectura de valid1.txt lance PermissionError aplicando patch dinámicamente
        original_open = open
        def side_effect(file, *args, **kwargs):
            if "valid1.txt" in str(file) and len(args) > 0 and "r" in args[0]:
                raise PermissionError("Acceso denegado simulado")
            return original_open(file, *args, **kwargs)

        with patch("builtins.open", side_effect=side_effect):
            # Ejecutar empaquetado
            result = self.mock_app._crear_packed_dat()

        # Debe fallar (False)
        self.assertFalse(result)

        # packed.dat previo debe seguir intacto y no corrupto
        self.assertTrue(Path("packed.dat").exists())
        with zipfile.ZipFile("packed.dat", "r") as zip_f:
            self.assertIn("old_file.txt", zip_f.namelist())

        # Debe haber llamado a showerror
        self.mock_showerror.assert_called_once()

    @patch("zipfile.ZipFile.write")
    def test_simulated_write_error(self, mock_zip_write):
        """Verifica que un error simulado de escritura detiene la compilación, limpia temporales y mantiene packed.dat original"""
        # Crear un packed.dat previo
        with zipfile.ZipFile("packed.dat", "w") as old_zip:
            old_zip.writestr("old_file.txt", "contenido viejo")

        # Crear un archivo de prueba
        with open("TRANSLATION_FILES_TO_PACK/valid1.txt", "w") as f:
            f.write("contenido")

        # Simular error de escritura en el ZipFile
        mock_zip_write.side_effect = IOError("Error de disco simulado")

        # Ejecutar empaquetado
        result = self.mock_app._crear_packed_dat()

        # Debe fallar (False)
        self.assertFalse(result)

        # No debe haber dejado un archivo temporal
        self.assertFalse(Path("packed.dat.tmp").exists())

        # packed.dat previo debe seguir intacto
        self.assertTrue(Path("packed.dat").exists())
        with zipfile.ZipFile("packed.dat", "r") as zip_f:
            self.assertIn("old_file.txt", zip_f.namelist())

        # Debe haber llamado a showerror
        self.mock_showerror.assert_called_once()


if __name__ == "__main__":
    unittest.main()
