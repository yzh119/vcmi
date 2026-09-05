# We need to keep this code into separate directory so CMake will execute it after all other subdirectories install code
# Otherwise we can't fix Mac bundle dependencies since binaries wouldn't be there when this code executed
if(MACOS)
	set(bundleDir "\${CMAKE_INSTALL_PREFIX}/${APP_BUNDLE_DIR}")
	set(bundleContentsDir "${bundleDir}/Contents")
	set(executablesDir "${bundleContentsDir}/MacOS")

	set(macdeployqtParams "\"${bundleDir}\"")
	if(ENABLE_EDITOR)
		string(APPEND macdeployqtParams " \"-executable=${executablesDir}/vcmieditor\"")
	endif()
	# note: cross-compiled Qt 5 builds macdeployqt for target platform instead of host
	vcmi_deploy_qt(macdeployqt "${macdeployqtParams}")

	# Homebrew ships sdl2-compat instead of SDL2: a shim that dlopen()s the real SDL3
	# at runtime. macdeployqt only follows link-time dependencies, so SDL3 never ends up
	# in the bundle and the app dies with "Failed loading SDL3 library.": dyld doesn't
	# search Homebrew's prefix for a bare library name and hardened runtime strips
	# DYLD_*_PATH, so there is no launch-time workaround either. sdl2-compat probes
	# @executable_path/libSDL3.dylib and @loader_path/libSDL3.dylib, so ship SDL3 ourselves.
	get_filename_component(sdl2LibraryRealPath "${SDL2_LIBRARY}" REALPATH)
	file(STRINGS "${sdl2LibraryRealPath}" sdl2CompatMarker REGEX "^libSDL3\\.dylib$" LIMIT_COUNT 1)
	if(sdl2CompatMarker)
		get_filename_component(sdl2LibraryDir "${sdl2LibraryRealPath}" DIRECTORY)
		find_library(SDL2_COMPAT_SDL3_LIBRARY NAMES SDL3 HINTS "${sdl2LibraryDir}")
		if(SDL2_COMPAT_SDL3_LIBRARY)
			get_filename_component(sdl3LibraryRealPath "${SDL2_COMPAT_SDL3_LIBRARY}" REALPATH)
			# must stay writable so that codesigning below can replace its signature
			install(FILES "${sdl3LibraryRealPath}"
				DESTINATION "${LIB_DIR}"
				RENAME libSDL3.dylib
				PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ
			)
			install(CODE "
				file(REMOVE \"${executablesDir}/libSDL3.dylib\")
				file(CREATE_LINK \"../Frameworks/libSDL3.dylib\" \"${executablesDir}/libSDL3.dylib\" SYMBOLIC)
			")

			# same problem when running straight from the build tree instead of the bundle
			if(TARGET vcmiclient)
				add_custom_target(sdl3_build_tree_link ALL
					COMMAND ${CMAKE_COMMAND} -E make_directory "$<TARGET_FILE_DIR:vcmiclient>"
					COMMAND ${CMAKE_COMMAND} -E remove -f "$<TARGET_FILE_DIR:vcmiclient>/libSDL3.dylib"
					COMMAND ${CMAKE_COMMAND} -E create_symlink "${SDL2_COMPAT_SDL3_LIBRARY}" "$<TARGET_FILE_DIR:vcmiclient>/libSDL3.dylib"
					VERBATIM
				)
			endif()
		else()
			message(WARNING "SDL2 is provided by sdl2-compat, but SDL3 was not found - VCMI will fail to start")
		endif()
	endif()

	# perform ad-hoc codesigning
	# Intel Macs don't need it
	if(CMAKE_SYSTEM_PROCESSOR STREQUAL "arm64")
		set(NEEDS_ADHOC_SIGNING 1)
	endif()

	set(executablesToSign vcmiserver)
	if(ENABLE_EDITOR)
		list(APPEND executablesToSign vcmieditor)
	endif()
	# main executable must be last
	list(APPEND executablesToSign vcmiclient)
	if(ENABLE_LAUNCHER)
		list(APPEND executablesToSign vcmilauncher)
	endif()

	set(codesignCommand "codesign --verbose=4 --force --options runtime --sign")
	install(CODE "
set(CODE_SIGN_IDENTITY \$ENV{MACOS_CODE_SIGN_IDENTITY})
if(NOT CODE_SIGN_IDENTITY AND \"${NEEDS_ADHOC_SIGNING}\")
	set(CODE_SIGN_IDENTITY \"-\")
	set(codesignParams --timestamp=none)
	set(codesignParamsForExecutables --entitlements \"${CMAKE_CURRENT_SOURCE_DIR}/entitlements_adhoc.plist\")
	message(\"performing adhoc signing\")
else()
	set(codesignParams --timestamp --strict)
endif()
if(CODE_SIGN_IDENTITY)
	execute_process(COMMAND
		bash -c \"
			for f in '${executablesDir}/vcmibuilder' $(find '${bundleContentsDir}' -type f -iname '*.dylib'); do
				${codesignCommand} '\${CODE_SIGN_IDENTITY}' $@ \\\"$f\\\"
			done
		\" \"\" \${codesignParams}
	)
	foreach(executable ${executablesToSign})
		execute_process(COMMAND
			${codesignCommand} \${CODE_SIGN_IDENTITY} \${codesignParams} --identifier eu.vcmi.\${executable} \${codesignParamsForExecutables} \"${executablesDir}/\${executable}\"
		)
	endforeach()
	if(NOT CODE_SIGN_IDENTITY STREQUAL \"-\")
		execute_process(COMMAND
			${codesignCommand} \${CODE_SIGN_IDENTITY} \${codesignParams} \"${bundleDir}\"
		)
	endif()
endif()
	")
endif()
